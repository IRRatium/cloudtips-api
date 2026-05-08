# Cards

## get_cards

Получить список привязанных карт.

```python
async def get_cards(self) -> List[Card]
```

### Пример

```python
async with CloudTipsClient(auth) as client:
    cards = await client.get_cards()
    for card in cards:
        print(card)
        # MIR *3742 (T-BANK, до 08/34) [по умолчанию]

        print(card.token)           # tk_89e6b3c6827afd4e9ccc36db2d22f
        print(card.card_type)       # MIR
        print(card.last_four)       # 3742
        print(card.issuer_code)     # T-BANK
        print(card.is_default)      # True
```

---

## delete_card

Удалить привязанную карту по токену.

```python
async def delete_card(self, card_token: str) -> bool
```

### Параметры

| Параметр | Тип | Описание |
|---|---|---|
| `card_token` | `str` | Токен карты (`card.token`) |

### Возвращает

`True` если удаление прошло успешно.

### Пример

```python
async with CloudTipsClient(auth) as client:
    cards = await client.get_cards()
    for card in cards:
        if not card.is_default:
            success = await client.delete_card(card.token)
            print(f"Карта {card} удалена: {success}")
```

---

## Объект Card

Смотри [модель Card](models/card.md).

| Поле | Тип | Описание |
|---|---|---|
| `token` | `str` | Токен для операций |
| `first_six` | `str` | Первые 6 цифр (BIN) |
| `last_four` | `str` | Последние 4 цифры |
| `card_type` | `str` | Тип карты: MIR / VISA / MASTERCARD |
| `expiration_date` | `str` | Дата истечения (MM/YY) |
| `issuer_code` | `str` | Название банка |
| `is_default` | `bool` | Карта по умолчанию для выплат |
| `commission_hint` | `str` | Подсказка о комиссии |
