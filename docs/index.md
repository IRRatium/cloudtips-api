<p align="center">
  <img src="https://static.tildacdn.com/tild3431-6231-4938-b464-663831306266/Horiz.svg" alt="CloudTips" height="80">
</p>

# CloudTips API

Неофициальная асинхронная Python-библиотека для [CloudTips](https://cloudtips.ru) — получение донатов, поллинг новых поступлений и автоматическое обновление токенов.

## Установка

```bash
pip install cloudtips
```

## Возможности

- **Получение донатов** — за произвольный период с автопагинацией
- **Поллинг** — три режима: async-генератор, async-колбэк, фоновая задача
- **Авто-рефреш токенов** — токен обновляется за 2 минуты до истечения
- **Профиль** — данные пользователя, метод выплат, лимиты
- **Карты** — просмотр привязанных карт, удаление
- **Баланс и комиссии** — сводка накоплений, информация о выводе
- **Полная типизация** — dataclass-модели для всех ответов API

## Быстрый старт

```python
import asyncio
import json
from cloudtips import CloudTipsAuth, CloudTipsClient, TokenData

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

async def main():
    async with CloudTipsClient(auth) as client:
        donations = await client.get_all_donations()
        for d in donations:
            print(d)

asyncio.run(main())
```

## Требования

- Python ≥ 3.9
- [aiohttp](https://docs.aiohttp.org/) ≥ 3.9

## Лицензия

MIT © 2026 IRRing
