# Polling

`poll()` — асинхронный генератор для бесконечного поллинга новых донатов. Отслеживает уже виденные `transaction_id`, поэтому дублей не будет.

## Сигнатура

```python
async def poll(
    self,
    interval: int = 30,
    since: Optional[datetime] = None,
    callback: Optional[Callable[[Donation], None]] = None,
) -> AsyncIterator[Donation]
```

### Параметры

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `interval` | `int` | `30` | Пауза между запросами в секундах |
| `since` | `datetime` | Сейчас | С какого момента начинать |
| `callback` | `Callable` | `None` | Если передан — метод блокируется и вызывает колбэк |

---

## Вариант 1 — async-генератор

Рекомендуемый способ. Итерируйте донаты по мере их поступления.

```python
async with CloudTipsClient(auth) as client:
    print("Слушаем новые донаты...")
    async for donation in client.poll(interval=30):
        print(f"💰 {donation.name} задонатил {donation.amount}₽")
        if donation.comment:
            print(f"   Комментарий: {donation.comment}")
```

---

## Вариант 2 — async-колбэк

Передайте `callback` — метод заблокируется и будет вызывать колбэк при каждом новом донате.

```python
async def handle_donation(donation: Donation):
    print(f"Новый донат от {donation.name}: {donation.amount}₽")
    # await bot.send_message(chat_id, str(donation))

async with CloudTipsClient(auth) as client:
    await client.poll(interval=15, callback=handle_donation)
```

Поддерживаются как `async def`, так и обычные `def` колбэки.

---

## Вариант 3 — фоновая задача asyncio

Запустите поллинг в фоне и параллельно выполняйте другую логику.

```python
async def poll_task(client: CloudTipsClient):
    async for donation in client.poll(interval=30):
        print(f"Новый донат: {donation}")

async def main():
    async with CloudTipsClient(auth) as client:
        task = asyncio.create_task(poll_task(client))
        # Основная логика бота, сервера и т.д.
        await asyncio.sleep(3600)  # работаем час
        task.cancel()

asyncio.run(main())
```

---

## Интеграция с Telegram-ботом

```python
import asyncio
from aiogram import Bot
from cloudtips import CloudTipsAuth, CloudTipsClient

bot = Bot(token="YOUR_BOT_TOKEN")

async def handle_donation(donation):
    await bot.send_message(
        chat_id=YOUR_CHAT_ID,
        text=f"💰 Новый донат!\n{donation.name} → {donation.amount}₽"
              + (f'\n"{donation.comment}"' if donation.comment else ""),
    )

async def main():
    async with CloudTipsClient(auth) as client:
        await client.poll(interval=15, callback=handle_donation)

asyncio.run(main())
```

> **Совет:** не ставьте `interval` меньше 10 секунд — это может привести к блокировке со стороны CloudTips.
