# AccumulationSummary

Сводка по накопленным средствам — баланс к выводу, комиссия, дата следующей выплаты.

## Определение

```python
@dataclass
class AccumulationSummary:
    accumulated_amount: float
    amount_to_deposit: float
    commission: float
    commission_percent: float
    next_payout_date: Optional[str]
    commission_hint: str
```

## Поля

| Поле | Тип | Описание |
|---|---|---|
| `accumulated_amount` | `float` | Накопленная сумма (₽) |
| `amount_to_deposit` | `float` | Сумма к выводу после вычета комиссии (₽) |
| `commission` | `float` | Размер комиссии (₽) |
| `commission_percent` | `float` | Процент комиссии |
| `next_payout_date` | `str \| None` | Дата следующей автоматической выплаты |
| `commission_hint` | `str` | Текст подсказки о комиссии |

## Пример использования

```python
s = await client.get_accumulation_summary()
print(f"Накоплено: {s.accumulated_amount}₽")
print(f"К выводу: {s.amount_to_deposit}₽")
print(f"Комиссия: {s.commission_percent}% ({s.commission}₽)")
print(f"Следующая выплата: {s.next_payout_date or 'не запланирована'}")
```

## from_dict

```python
@classmethod
def from_dict(cls, data: dict) -> "AccumulationSummary"
```
