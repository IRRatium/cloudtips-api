# Card

Представляет привязанную банковскую карту.

## Определение

```python
@dataclass
class Card:
    token: str
    first_six: str
    last_four: str
    card_type: str
    expiration_date: str
    issuer_code: str
    is_default: bool
    commission_hint: str
```

## Поля

| Поле | Тип | Описание |
|---|---|---|
| `token` | `str` | Токен карты для операций |
| `first_six` | `str` | Первые 6 цифр (BIN) |
| `last_four` | `str` | Последние 4 цифры |
| `card_type` | `str` | Тип: `MIR` / `VISA` / `MASTERCARD` |
| `expiration_date` | `str` | Дата истечения в формате `MM/YY` |
| `issuer_code` | `str` | Название банка-эмитента |
| `is_default` | `bool` | Является ли картой по умолчанию |
| `commission_hint` | `str` | Текст подсказки о комиссии |

## Строковое представление

```python
str(card)
# "MIR *3742 (T-BANK, до 08/34) [по умолчанию]"
# "VISA *1234 (SBER, до 12/26)"
```

## Пример использования

```python
cards = await client.get_cards()
for card in cards:
    print(card)
    print(card.token)           # tk_89e6b3c6827afd4e9ccc36db2d22f
    print(card.card_type)       # MIR
    print(card.last_four)       # 3742
    print(card.issuer_code)     # T-BANK
    print(card.is_default)      # True
    print(card.expiration_date) # 08/34

# Удаление неосновных карт
for card in cards:
    if not card.is_default:
        await client.delete_card(card.token)
```

## from_dict

```python
@classmethod
def from_dict(cls, data: dict) -> "Card"
```
