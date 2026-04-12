# CloudtipsAPI

Неофициальная Python-библиотека для [CloudTips](https://cloudtips.ru) — получение донатов, поллинг новых поступлений и автоматическое обновление токенов.

## Установка

```bash
pip install cloudtips
```

## Быстрый старт

```python
import json
from cloudtips import CloudTipsAuth, CloudTipsClient, TokenData

# Загружаем токены из файла (donate.json или своего хранилища)
with open("donate.json") as f:
    config = json.load(f)

# Колбэк вызывается каждый раз при обновлении токенов.
# Refresh-токен одноразовый — обязательно сохраняйте новые!
def on_token_refresh(token_data: TokenData):
    config["cloudtips_token"] = token_data.access_token
    config["cloudtips_refresh_token"] = token_data.refresh_token
    config["cloudtips_expires_at"] = token_data.expires_at
    with open("donate.json", "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("Токены обновлены и сохранены.")

auth = CloudTipsAuth(
    token=config["cloudtips_token"],
    refresh_token=config["cloudtips_refresh_token"],
    expires_at=config["cloudtips_expires_at"],
    on_token_refresh=on_token_refresh,
)

client = CloudTipsClient(auth)
```

## Получение донатов

```python
# Все донаты
donations = client.get_all_donations()
for d in donations:
    print(d)  # [2026-04-10 20:44] евгения → 50₽ — "оч крутой сервис"

# Только за последние сутки
from datetime import datetime, timedelta, timezone

yesterday = datetime.now(tz=timezone.utc) - timedelta(days=1)
recent = client.get_donations(since=yesterday)
```

## Поллинг новых донатов

### Вариант 1 — генератор (блокирует поток)

```python
print("Слушаем новые донаты...")
for donation in client.poll(interval=30):
    print(f"💰 {donation.name} задонатил {donation.amount}₽")
    if donation.comment:
        print(f"   Комментарий: {donation.comment}")
```

### Вариант 2 — колбэк

```python
def handle_donation(donation):
    print(f"Новый донат от {donation.name}: {donation.amount}₽")

# Блокирующий вызов, удобно для простых скриптов
client.poll(interval=15, callback=handle_donation)
```

### Вариант 3 — в отдельном потоке

```python
import threading

thread = threading.Thread(
    target=client.poll,
    kwargs={"interval": 30, "callback": handle_donation},
    daemon=True,
)
thread.start()

# Основная логика программы продолжается...
```

## Структура `Donation`

```python
@dataclass
class Donation:
    transaction_id: int    # уникальный ID транзакции
    name: str              # имя донатера
    amount: int            # сумма в рублях
    tg_id: int             # Telegram ID
    comment: str           # комментарий (может быть пустым)
    date: datetime         # дата и время

str(donation)
# "[2026-04-10 23:04] Каспер → 200₽ — "спасибо за отличный сервис)""
```

## Обработка ошибок

```python
from cloudtips import CloudTipsAuthError, CloudTipsAPIError

try:
    donations = client.get_donations()
except CloudTipsAuthError as e:
    print(f"Проблема с аутентификацией: {e}")
except CloudTipsAPIError as e:
    print(f"Ошибка API (HTTP {e.status_code}): {e.detail}")
```

## Примечания

- **Refresh-токен одноразовый.** После каждого обновления старый токен становится недействительным. Всегда передавайте `on_token_refresh` и сохраняйте новые токены.
- Библиотека автоматически обновляет токен за 2 минуты до истечения.
- Поллинг отслеживает уже виденные `transaction_id`, поэтому дублей не будет.

## Лицензия

MIT
