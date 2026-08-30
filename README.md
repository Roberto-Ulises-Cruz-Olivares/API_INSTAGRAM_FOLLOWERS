# API_INSTAGRAM_FOLLOWERS ------> DEMO VERSION 1

Una API simple y eficiente que extrae todos los seguidores de un usuario específico en Instagram.

## Requisitos

Necesitas tener los 3 tokens de inicio de sesión de tu cuenta activa:

- SESSIONID
- CSRFTOKEN
- DS_USER_ID

Una vez extraídas las credenciales, ponerlas de la siguiente forma en la terminal:

```powershell
$env:IG_SESSIONID="TOKEN_AQUI"
$env:IG_CSRFTOKEN="TOKEN_AQUI"
$env:IG_DS_USER_ID="TOKEN_AQUI"
```

## Notas

- El usuario debe tener la cuenta pública o seguirte para poder extraer los followers.
- Muchas peticiones al servidor de Instagram banearán tu ID durante 1 semana aproximadamente.
