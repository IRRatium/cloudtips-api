# TokenData

Объект с обновлёнными токенами, передаваемый в колбэк `on_token_refresh`.

## Определение

```python
@dataclass
class TokenData:
    access_token: str
    refresh_token: str
    expires_at: float
```

## Поля

| Поле | Тип | Описание |
|---|---|---|
| `access_token` | `str` | Новый access-токен |
| `refresh_token` | `str` | Новый refresh-токен (одноразовый) |
| `expires_at` | `float` | Unix timestamp истечения access-токена |

## Использование в on_token_refresh

```python
async def on_token_refresh(token_data: TokenData):
    # Обязательно сохраните все три значения!
    config["cloudtips_token"] = token_data.access_token
    config["cloudtips_refresh_token"] = token_data.refresh_token
    config["cloudtips_expires_at"] = token_data.expires_at
    with open("donate.json", "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
```

!!! danger "Важно"
    Refresh-токен **одноразовый**. После получения `TokenData` обязательно
    сохраните все три поля. Если потерять `refresh_token` — придётся
    заново получать токены из браузера.
