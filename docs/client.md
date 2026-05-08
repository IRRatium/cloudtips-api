# Client Overview

`CloudTipsClient` — основной класс для работы с CloudTips API.

## Создание клиента

```python
from cloudtips import CloudTipsAuth, CloudTipsClient

client = CloudTipsClient(auth)
```

### Параметры конструктора

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `auth` | `CloudTipsAuth` | — | Объект аутентификации |
| `base_url` | `str` | `https://api.cloudtips.ru/api` | Базовый URL API |

## Управление сессией

### Рекомендуемый способ — контекстный менеджер

```python
async with CloudTipsClient(auth) as client:
    donations = await client.get_all_donations()
```

### Ручное управление

```python
client = CloudTipsClient(auth)
await client.open()
try:
    donations = await client.get_all_donations()
finally:
    await client.close()
```

### Методы сессии

| Метод | Описание |
|---|---|
| `await client.open()` | Открыть aiohttp-сессию |
| `await client.close()` | Закрыть aiohttp-сессию |

## Доступные методы

### Донаты

| Метод | Описание |
|---|---|
| [`get_donations(...)`](donations.md) | Получить донаты за период (одна страница) |
| [`get_all_donations(...)`](donations.md) | Получить все донаты с автопагинацией |
| [`poll(...)`](polling.md) | Бесконечный поллинг новых донатов |

### Профиль

| Метод | Описание |
|---|---|
| [`get_me()`](profile.md) | Получить профиль текущего пользователя |

### Карты

| Метод | Описание |
|---|---|
| [`get_cards()`](cards.md) | Список привязанных карт |
| [`delete_card(card_token)`](cards.md) | Удалить карту |

### Выплаты и баланс

| Метод | Описание |
|---|---|
| [`get_accumulation_summary()`](payouts.md) | Сводка накоплений и баланс |
| [`get_payout_fee_info()`](payouts.md) | Информация о комиссиях |
| [`get_payout_method()`](payouts.md) | Текущий метод выплат |
| [`set_payout_method(method)`](payouts.md) | Установить метод выплат |
