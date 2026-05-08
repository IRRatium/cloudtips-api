# ReceiverProfile

Профиль текущего авторизованного пользователя CloudTips.

## Определение

```python
@dataclass
class ReceiverProfile:
    user_id: str
    full_name: str
    phone_number: str
    photo_url: str
    payout_method: str
    instant_payout_enabled: bool
    is_premium: bool
    onboarding_passed: bool
    gender: str
    work_place: Optional[str]
    work_position: Optional[str]
    birthday: Optional[str]
    created_date: str
    available_amount_min: float
    available_amount_max: float
```

## Поля

| Поле | Тип | Описание |
|---|---|---|
| `user_id` | `str` | Уникальный ID пользователя |
| `full_name` | `str` | Полное имя |
| `phone_number` | `str` | Номер телефона |
| `photo_url` | `str` | URL фотографии профиля |
| `payout_method` | `str` | Метод выплат: `"Instant"` или `"Accumulation"` |
| `instant_payout_enabled` | `bool` | Доступны мгновенные выплаты |
| `is_premium` | `bool` | Наличие премиум-подписки |
| `onboarding_passed` | `bool` | Пройден ли онбординг |
| `gender` | `str` | Пол (`"NotSpecified"` / `"Male"` / `"Female"`) |
| `work_place` | `str \| None` | Место работы |
| `work_position` | `str \| None` | Должность |
| `birthday` | `str \| None` | Дата рождения |
| `created_date` | `str` | Дата регистрации |
| `available_amount_min` | `float` | Минимальная сумма выплаты (₽) |
| `available_amount_max` | `float` | Максимальная сумма выплаты (₽) |

## Строковое представление

```python
str(me)
# "IRRing (+79991234567)
# Метод выплат: Accumulation | Премиум: да | Лимиты: 100.0₽ — 75000.0₽"
```

## from_dict

```python
@classmethod
def from_dict(cls, data: dict) -> "ReceiverProfile"
```
