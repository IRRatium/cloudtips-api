# CloudtipsAPI
<p align="center">
  <img src="https://static.tildacdn.com/tild3431-6231-4938-b464-663831306266/Horiz.svg" alt="CloudTips" height="120">
</p>

<p align="center">
  <a href="https://pypi.org/project/cloudtips/"><img src="https://img.shields.io/pypi/v/cloudtips?color=blue&label=PyPI" alt="PyPI"></a>
  <a href="https://pepy.tech/project/cloudtips"><img src="https://static.pepy.tech/badge/cloudtips" alt="Downloads"></a>
  <a href="https://github.com/IRRatium/cloudtips-api/blob/main/LICENSE"><img src="https://img.shields.io/github/license/IRRatium/cloudtips-api" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.9+-blue" alt="Python 3.9+">
  <a href="https://docs.cloudtips.irring.ru"><img src="https://img.shields.io/badge/docs-docs.cloudtips.irring.ru-blue" alt="Docs"></a>
</p>

Неофициальная асинхронная Python-библиотека для [CloudTips](https://cloudtips.ru) — получение донатов, поллинг новых поступлений и автоматическое обновление токенов.

## Установка

```bash
pip install cloudtips
```

## Быстрый старт

```python
import asyncio
import json
from cloudtips import CloudTipsAuth, CloudTipsClient, TokenData

with open("donate.json") as f:
    config = json.load(f)

# Колбэк вызывается каждый раз при обновлении токенов.
# Поддерживаются как async, так и обычные функции.
# Refresh-токен одноразовый — обязательно сохраняйте новые!
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
        # [2026-04-10 20:44] евгения → 50₽ — "оч крутой сервис"

asyncio.run(main())
```

## Получение донатов

```python
async with CloudTipsClient(auth) as client:
    # Все донаты за последние 24 часа
    donations = await client.get_all_donations()
    for d in donations:
        print(d.name)     # евгения
        print(d.amount)   # 50
        print(d.comment)  # оч крутой сервис
        print(d.date)     # 2026-04-10 20:44:00+03:00

    # За конкретный период
    from datetime import datetime, timedelta, timezone

    week_ago = datetime.now(tz=timezone.utc) - timedelta(days=7)
    weekly = await client.get_all_donations(since=week_ago)
    print(f"Всего за неделю: {len(weekly)} донатов")
    print(f"Сумма: {sum(d.amount for d in weekly)}₽")
```

## Поллинг новых донатов

### Вариант 1 — async-генератор

```python
async with CloudTipsClient(auth) as client:
    async for donation in client.poll(interval=30):
        print(f"💰 {donation.name} задонатил {donation.amount}₽")
        if donation.comment:
            print(f"   Комментарий: {donation.comment}")
```

### Вариант 2 — async-колбэк

```python
async def handle_donation(donation):
    print(f"Новый донат от {donation.name}: {donation.amount}₽")
    # await bot.send_message(...)

async with CloudTipsClient(auth) as client:
    await client.poll(interval=15, callback=handle_donation)
```

### Вариант 3 — фоновая задача asyncio

```python
async def poll_task(client):
    async for donation in client.poll(interval=30):
        print(f"Новый донат: {donation}")

async def main():
    async with CloudTipsClient(auth) as client:
        task = asyncio.create_task(poll_task(client))
        await task

asyncio.run(main())
```

## Профиль, карты и баланс

```python
async with CloudTipsClient(auth) as client:
    # Профиль пользователя
    me = await client.get_me()
    print(me.full_name)       # IRRing
    print(me.payout_method)   # Accumulation

    # Привязанные карты
    for card in await client.get_cards():
        print(card)  # MIR *3742 (T-BANK, до 08/34) [по умолчанию]

    # Баланс к выводу
    s = await client.get_accumulation_summary()
    print(f"Накоплено: {s.accumulated_amount}₽")
    print(f"Комиссия: {s.commission_percent}%")
    print(f"Следующая выплата: {s.next_payout_date or 'не запланирована'}")

    # Информация о комиссиях
    fee = await client.get_payout_fee_info()
    print(fee.text)

    # Смена метода выплат
    await client.set_payout_method("Instant")       # мгновенно
    await client.set_payout_method("Accumulation")  # накопительно

    # Удаление карты
    for card in await client.get_cards():
        if not card.is_default:
            await client.delete_card(card.token)
```

## Обработка ошибок

```python
from cloudtips import CloudTipsAuthError, CloudTipsAPIError

try:
    async with CloudTipsClient(auth) as client:
        donations = await client.get_all_donations()
except CloudTipsAuthError as e:
    print(f"Проблема с аутентификацией: {e}")
except CloudTipsAPIError as e:
    print(f"Ошибка API (HTTP {e.status_code}): {e.detail}")
```

## Примечания

- **Refresh-токен одноразовый.** После каждого обновления старый токен становится недействительным. Всегда передавайте `on_token_refresh` и сохраняйте новые токены.
- `on_token_refresh` поддерживает как обычные (`def`), так и async-функции (`async def`).
- Библиотека автоматически обновляет токен за 2 минуты до истечения.
- Поллинг отслеживает уже виденные `transaction_id`, поэтому дублей не будет.
- Клиент — контекстный менеджер (`async with`), это рекомендуемый способ использования.

## Лицензия

MIT
