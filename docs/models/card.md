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
# "MIR *0000 (BANK, до 01/28) [по умолчанию]"
# "VISA *0000 (BANK, до 12/26)"
```

## Пример использования

```python
cards = await client.get_cards()
for card in cards:
    print(card)
    print(card.token)           # tk_...
    print(card.card_type)       # MIR
    print(card.last_four)       # 0000
    print(card.issuer_code)     # BANK
    print(card.is_default)      # True
    print(card.expiration_date) # 01/28

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
