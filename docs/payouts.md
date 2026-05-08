# Payouts & Balance

## get_accumulation_summary

Получить сводку по накопленным средствам — баланс к выводу, комиссия, дата следующей выплаты.

```python
async def get_accumulation_summary(self) -> AccumulationSummary
```

### Пример

```python
async with CloudTipsClient(auth) as client:
    s = await client.get_accumulation_summary()
    print(f"Накоплено: {s.accumulated_amount}₽")
    print(f"К выводу: {s.amount_to_deposit}₽")
    print(f"Комиссия: {s.commission_percent}% ({s.commission}₽)")
    print(f"Следующая выплата: {s.next_payout_date or 'не запланирована'}")
```

---

## get_payout_fee_info

Получить информацию о комиссиях при выводе средств.

```python
async def get_payout_fee_info(self) -> PayoutFeeInfo
```

### Пример

```python
async with CloudTipsClient(auth) as client:
    fee = await client.get_payout_fee_info()
    print(fee.text)
    print(fee.tinkoff_commission_hint)
    print(fee.instant_payout_commission_text)
```

---

## get_payout_method

Получить текущий метод выплат.

```python
async def get_payout_method(self) -> str
```

Возвращает `"Instant"` или `"Accumulation"`.

```python
async with CloudTipsClient(auth) as client:
    method = await client.get_payout_method()
    print(method)  # Accumulation
```

---

## set_payout_method

Установить метод выплат.

```python
async def set_payout_method(self, method: str = "Instant") -> bool
```

### Параметры

| Параметр | Тип | Описание |
|---|---|---|
| `method` | `str` | `"Instant"` — мгновенно, `"Accumulation"` — накопительно |

### Пример

```python
async with CloudTipsClient(auth) as client:
    await client.set_payout_method("Instant")       # мгновенные выплаты
    await client.set_payout_method("Accumulation")  # накопительные выплаты
```

---

## Объекты ответов

- [AccumulationSummary](models/accumulation_summary.md)
- [PayoutFeeInfo](models/payout_fee_info.md)
