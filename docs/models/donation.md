# Donation

Представляет один донат (транзакцию) в CloudTips.

## Определение

```python
@dataclass
class Donation:
    transaction_id: int
    name: str
    amount: int
    tg_id: int
    comment: str
    date: datetime
```

## Поля

| Поле | Тип | Описание |
|---|---|---|
| `transaction_id` | `int` | Уникальный ID транзакции |
| `name` | `str` | Имя донатера (`"Аноним"` если не указано) |
| `amount` | `int` | Сумма в рублях |
| `tg_id` | `int` | Telegram ID донатера (0 если нет) |
| `comment` | `str` | Комментарий (пустая строка если нет) |
| `date` | `datetime` | Дата и время доната |

## Строковое представление

```python
str(donation)
# "[2026-04-10 23:04] Каспер → 200₽ — "спасибо за отличный сервис)""

# Без комментария:
# "[2026-04-10 20:44] Аноним → 100₽"
```

## Пример использования

```python
donations = await client.get_all_donations()

for d in donations:
    print(d.name)            # Каспер
    print(d.amount)          # 200
    print(d.comment)         # спасибо за отличный сервис)
    print(d.date)            # 2026-04-10 23:04:00+03:00
    print(d.transaction_id)  # 1234567

    # Суммарный доход
    total = sum(d.amount for d in donations)
    print(f"Итого: {total}₽")
```

## from_dict

Фабричный метод для создания объекта из словаря API-ответа.

```python
@classmethod
def from_dict(cls, data: dict) -> "Donation"
```
