# Donations

## get_donations

Получить донаты за период через `/timeline`. Возвращает одну страницу результатов.

```python
async def get_donations(
    self,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    limit: int = 50,
    page: int = 1,
) -> List[Donation]
```

### Параметры

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `since` | `datetime` | 24 часа назад | Начало периода |
| `until` | `datetime` | Сейчас | Конец периода |
| `limit` | `int` | `50` | Количество на страницу |
| `page` | `int` | `1` | Номер страницы |

### Пример

```python
from datetime import datetime, timedelta, timezone

async with CloudTipsClient(auth) as client:
    # За последние 24 часа (по умолчанию)
    donations = await client.get_donations()

    # За конкретный период
    yesterday = datetime.now(tz=timezone.utc) - timedelta(days=1)
    donations = await client.get_donations(since=yesterday)

    # Вторая страница
    page2 = await client.get_donations(page=2)
```

---

## get_all_donations

Получить **все** донаты за период с автоматической пагинацией. Результат отсортирован по дате.

```python
async def get_all_donations(
    self,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> List[Donation]
```

### Параметры

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `since` | `datetime` | 24 часа назад | Начало периода |
| `until` | `datetime` | Сейчас | Конец периода |

### Пример

```python
from datetime import datetime, timedelta, timezone

async with CloudTipsClient(auth) as client:
    # Все за последние 24 часа
    donations = await client.get_all_donations()
    for d in donations:
        print(d)
    # [2026-04-10 20:44] евгения → 50₽ — "оч крутой сервис"

    # За неделю
    week_ago = datetime.now(tz=timezone.utc) - timedelta(days=7)
    weekly = await client.get_all_donations(since=week_ago)
    print(f"Всего за неделю: {len(weekly)} донатов")
    print(f"Сумма: {sum(d.amount for d in weekly)}₽")
```

---

## Объект Donation

Смотри [модель Donation](models/donation.md).

```python
print(donation)
# [2026-04-10 23:04] Каспер → 200₽ — "спасибо за отличный сервис)"

print(donation.name)    # Каспер
print(donation.amount)  # 200
print(donation.comment) # спасибо за отличный сервис)
print(donation.date)    # 2026-04-10 23:04:00+03:00
```
