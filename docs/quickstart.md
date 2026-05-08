# Quickstart

## Установка

```bash
pip install cloudtips
```

## Шаг 1 — Получите токены

Токены CloudTips можно получить из локального хранилища браузера на сайте [lk.cloudtips.ru](https://lk.cloudtips.ru):

1. Войдите в личный кабинет
2. Откройте DevTools → Application → Local Storage
3. Найдите ключи `access_token`, `refresh_token`, `expires_at`

Сохраните их в файл `donate.json`:

```json
{
  "cloudtips_token": "eyJ...",
  "cloudtips_refresh_token": "abc123...",
  "cloudtips_expires_at": 1776099728.0
}
```

## Шаг 2 — Создайте клиент

```python
import json
from cloudtips import CloudTipsAuth, CloudTipsClient, TokenData

with open("donate.json") as f:
    config = json.load(f)

# Колбэк для сохранения новых токенов (refresh-токен одноразовый!)
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

## Шаг 3 — Используйте API

```python
import asyncio

async def main():
    async with CloudTipsClient(auth) as client:
        # Донаты за последние 24 часа
        donations = await client.get_all_donations()
        for d in donations:
            print(d)
        # [2024-01-15 14:30] Алексей → 100₽ — "спасибо за контент"

        # Профиль
        me = await client.get_me()
        print(me.full_name)

        # Баланс
        s = await client.get_accumulation_summary()
        print(f"Накоплено: {s.accumulated_amount}₽")

asyncio.run(main())
```

!!! note "Важно"
    Передавайте `on_token_refresh` и обязательно сохраняйте новые токены.
    Refresh-токен **одноразовый** — после использования старый становится недействительным.
