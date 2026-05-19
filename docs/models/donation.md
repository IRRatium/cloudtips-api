# Donation

Представляет один донат (транзакцию) в CloudTips.

## Определение

```python
@dataclass
class Donation:
    transaction_id: int
    name: str
    amount: float
    comment: str
    date: datetime
```

## Поля

| Поле | Тип | Описание |
|---|---|---|
| `transaction_id` | `int` | Уникальный ID транзакции |
| `name` | `str` | Имя донатера (`"Аноним"` если не указано) |
| `amount` | `float` | Сумма в рублях |
| `comment` | `str` | Комментарий (пустая строка если нет) |
| `date` | `datetime` | Дата и время доната |

## Строковое представление

```python
str(donation)
# "[2024-01-15 14:30] Алексей → 500₽ — "отличная работа!""

# Без комментария:
# "[2024-01-15 20:44] Аноним → 100₽"
```

## Пример использования

```python
donations = await client.get_all_donations()

for d in donations:
    print(d.name)            # Алексей
    print(d.amount)          # 500.0
    print(d.comment)         # отличная работа!
    print(d.date)            # 2024-01-15 14:30:00+03:00
    print(d.transaction_id)  # 1234567

total = sum(d.amount for d in donations)
print(f"Итого: {total}₽")
```

## from_dict

Фабричный метод для создания объекта из словаря API-ответа.

```python
@classmethod
def from_dict(cls, data: dict) -> "Donation"
```
