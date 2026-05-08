# PayoutFeeInfo

Информация о комиссиях при выводе средств.

## Определение

```python
@dataclass
class PayoutFeeInfo:
    text: str
    downgrade_condition: str
    tinkoff_commission_hint: str
    instant_payout_commission_text: str
```

## Поля

| Поле | Тип | Описание |
|---|---|---|
| `text` | `str` | Основной текст о комиссии |
| `downgrade_condition` | `str` | Условие снижения комиссии |
| `tinkoff_commission_hint` | `str` | Подсказка для карт T-Bank |
| `instant_payout_commission_text` | `str` | Текст о комиссии при мгновенном выводе |

## Пример использования

```python
fee = await client.get_payout_fee_info()
print(fee.text)
print(fee.tinkoff_commission_hint)
print(fee.instant_payout_commission_text)
```

## from_dict

```python
@classmethod
def from_dict(cls, data: dict) -> "PayoutFeeInfo"
```
