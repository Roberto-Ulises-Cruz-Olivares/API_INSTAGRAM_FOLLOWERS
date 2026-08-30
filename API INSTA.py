#!/usr/bin/env python3
"""
Descarga la lista completa de seguidores de un perfil de Instagram
usando los endpoints internos de la web, con TU propia sesión.

Uso:
    export IG_SESSIONID="..."
    export IG_CSRFTOKEN="..."
    export IG_DS_USER_ID="..."
    python instagram_followers.py <username>

Requiere:  pip install requests
"""

import os
import sys
import csv
import json
import time
import random
import argparse
import requests

APP_ID = "936619743392459"          # x-ig-app-id clasico de instagram web
BASE = "https://www.instagram.com/api/v1"


def build_session():
    faltan = [v for v in ("IG_SESSIONID", "IG_CSRFTOKEN", "IG_DS_USER_ID")
              if not os.environ.get(v)]
    if faltan:
        sys.exit(f"Faltan variables de entorno: {', '.join(faltan)}")

    s = requests.Session()
    s.headers.update({
        "x-ig-app-id": APP_ID,
        "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/149.0.0.0 Safari/537.36"),
        "x-csrftoken": os.environ["IG_CSRFTOKEN"],
        "referer": "https://www.instagram.com/",
    })
    s.cookies.update({
        "sessionid": os.environ["IG_SESSIONID"],
        "csrftoken": os.environ["IG_CSRFTOKEN"],
        "ds_user_id": os.environ["IG_DS_USER_ID"],
    })
    return s


def get_user_id(s, username):
    r = s.get(f"{BASE}/users/web_profile_info/", params={"username": username})
    if r.status_code != 200:
        sys.exit(f"No pude resolver el usuario (HTTP {r.status_code}). "
                 "Revisa que las cookies sigan vigentes y el username sea correcto.")
    user = r.json()["data"]["user"]
    #print("STATUS:", r.status_code)
    #print("RAW:", r.text[:500])
    return user["id"], user


def pedir_pagina(s, user_id, max_id, count):
    params = {"count": count}
    if max_id:
        params["max_id"] = max_id

    espera = 30  # segundos, se duplica en cada reintento
    for _ in range(5):
        r = s.get(f"{BASE}/friendships/{user_id}/followers/", params=params)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429 or r.status_code >= 500:
            print(f"  rate limit / error {r.status_code}: espero {espera}s...")
            time.sleep(espera)
            espera = min(espera * 2, 600)
            continue
        sys.exit(f"Error {r.status_code}: {r.text[:200]}")

    sys.exit("Demasiados reintentos seguidos; conviene parar y volver mas tarde.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("username", help="perfil objetivo")
    ap.add_argument("--count", type=int, default=25, help="por pagina (default 25)")
    ap.add_argument("--min-delay", type=float, default=2.0)
    ap.add_argument("--max-delay", type=float, default=5.0)
    args = ap.parse_args()

    s = build_session()
    user_id, info = get_user_id(s, args.username)
    total = info.get("edge_followed_by", {}).get("count")
    privado = info.get("is_private")
    print(f"@{args.username}  id={user_id}  seguidores~{total}  privado={privado}")
    if privado:
        print("Ojo: es privado. Solo veras la lista si tu cuenta lo sigue y fue aceptada.")

    salida_csv = f"followers_{args.username}.csv"
    checkpoint = f".ckpt_{args.username}.json"

    # reanudar si quedo una corrida a medias
    max_id, vistos = None, set()
    if os.path.exists(checkpoint):
        with open(checkpoint) as f:
            ck = json.load(f)
        max_id = ck.get("max_id")
        vistos = set(ck.get("vistos", []))
        print(f"Reanudando: {len(vistos)} ya guardados.")

    f = open(salida_csv, "a", newline="", encoding="utf-8")
    w = csv.writer(f)
    if os.path.getsize(salida_csv) == 0:
        w.writerow(["pk", "username", "full_name", "is_private", "is_verified"])

    pagina = 0
    while True:
        data = pedir_pagina(s, user_id, max_id, args.count)
        users = data.get("users", [])
        nuevos = 0
        for u in users:
            if u["pk"] in vistos:
                continue
            vistos.add(u["pk"])
            nuevos += 1
            w.writerow([u["pk"], u["username"], u.get("full_name", ""),
                        u.get("is_private"), u.get("is_verified")])
        f.flush()
        pagina += 1
        print(f"  pagina {pagina}: +{nuevos}  (total {len(vistos)})")

        max_id = data.get("next_max_id")
        with open(checkpoint, "w") as c:
            json.dump({"max_id": max_id, "vistos": list(vistos)}, c)

        if not max_id:
            break
        time.sleep(random.uniform(args.min_delay, args.max_delay))

    f.close()
    if os.path.exists(checkpoint):
        os.remove(checkpoint)
    print(f"\nListo: {len(vistos)} seguidores guardados en {salida_csv}")
    


if __name__ == "__main__":
    main()
