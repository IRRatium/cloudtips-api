# Profile

## get_me

Получить профиль текущего авторизованного пользователя.

```python
async def get_me(self) -> ReceiverProfile
```

### Пример

```python
async with CloudTipsClient(auth) as client:
    me = await client.get_me()
    print(me.full_name)              # IRRing
    print(me.phone_number)           # +7 (999) 123-45-67
    print(me.payout_method)          # Accumulation
    print(me.is_premium)             # True
    print(me.available_amount_min)   # 100.0
    print(me.available_amount_max)   # 75000.0
    print(me)
    # IRRing (+79991234567)
    # Метод выплат: Accumulation | Премиум: да | Лимиты: 100.0₽ — 75000.0₽
```

---

## Объект ReceiverProfile

Смотри [модель ReceiverProfile](models/receiver_profile.md).

| Поле | Тип | Описание |
|---|---|---|
| `user_id` | `str` | ID пользователя |
| `full_name` | `str` | Полное имя |
| `phone_number` | `str` | Номер телефона |
| `photo_url` | `str` | URL аватара |
| `payout_method` | `str` | Метод выплат: `"Instant"` / `"Accumulation"` |
| `instant_payout_enabled` | `bool` | Доступны мгновенные выплаты |
| `is_premium` | `bool` | Наличие премиум-статуса |
| `onboarding_passed` | `bool` | Пройден ли онбординг |
| `gender` | `str` | Пол |
| `work_place` | `str \| None` | Место работы |
| `work_position` | `str \| None` | Должность |
| `birthday` | `str \| None` | Дата рождения |
| `created_date` | `str` | Дата регистрации |
| `available_amount_min` | `float` | Минимальная сумма выплаты (₽) |
| `available_amount_max` | `float` | Максимальная сумма выплаты (₽) |
