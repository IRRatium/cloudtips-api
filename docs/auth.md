# Authentication

`CloudTipsAuth` управляет access/refresh токенами и автоматически обновляет их за 2 минуты до истечения.

## Класс CloudTipsAuth

```python
class CloudTipsAuth:
    def __init__(
        self,
        token: str,
        refresh_token: str,
        expires_at: float,
        on_token_refresh: Optional[Callable[[TokenData], None]] = None,
    ) -> None
```

### Параметры

| Параметр | Тип | Описание |
|---|---|---|
| `token` | `str` | Access-токен CloudTips |
| `refresh_token` | `str` | Refresh-токен (одноразовый) |
| `expires_at` | `float` | Unix timestamp истечения access-токена |
| `on_token_refresh` | `Callable` | Колбэк при обновлении токенов (опционально) |

### Методы

#### `get_token() → str`

Возвращает актуальный access-токен. Если токен истёк или истекает в течение 2 минут — автоматически вызывает `refresh()`.

```python
token = await auth.get_token()
```

#### `refresh() → TokenData`

Принудительно обновляет токены через CloudTips Identity Server. Вызывает `on_token_refresh` с новыми данными.

```python
token_data = await auth.refresh()
```

#### `headers() → dict`

Возвращает готовые HTTP-заголовки для запросов к API.

```python
headers = await auth.headers()
# {"Authorization": "Bearer eyJ...", "Content-Type": "application/json"}
```

## Колбэк on_token_refresh

Поддерживаются как обычные, так и async-функции:

```python
# Async-колбэк (рекомендуется)
async def on_token_refresh(token_data: TokenData):
    await save_to_db(token_data)

# Обычный колбэк
def on_token_refresh(token_data: TokenData):
    save_to_file(token_data)
```

## Полный пример

```python
import json
from cloudtips import CloudTipsAuth, TokenData

with open("donate.json") as f:
    config = json.load(f)

async def on_token_refresh(token_data: TokenData):
    config["cloudtips_token"] = token_data.access_token
    config["cloudtips_refresh_token"] = token_data.refresh_token
    config["cloudtips_expires_at"] = token_data.expires_at
    with open("donate.json", "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

auth = CloudTipsAuth(
    token=config["cloudtips_token"],
    refresh_token=config["cloudtips_refresh_token"],
    expires_at=config["cloudtips_expires_at"],
    on_token_refresh=on_token_refresh,
)
```

!!! warning "Refresh-токен одноразовый"
    После каждого обновления старый refresh-токен становится недействительным.
    Всегда передавайте `on_token_refresh` и сохраняйте новые значения.
