# Errors

Библиотека использует два типа исключений.

## CloudTipsAPIError

Ошибка запроса к CloudTips API (HTTP-уровень).

```python
class CloudTipsAPIError(Exception):
    status_code: int   # HTTP-статус
    detail: object     # тело ответа (dict или str)
```

### Пример

```python
from cloudtips import CloudTipsAPIError

try:
    async with CloudTipsClient(auth) as client:
        donations = await client.get_all_donations()
except CloudTipsAPIError as e:
    print(f"Ошибка API (HTTP {e.status_code}): {e.detail}")
```

---

## CloudTipsAuthError

Ошибка аутентификации — возникает при неудачном обновлении токенов.

```python
class CloudTipsAuthError(Exception):
    ...
```

### Пример

```python
from cloudtips import CloudTipsAuthError

try:
    async with CloudTipsClient(auth) as client:
        await client.get_me()
except CloudTipsAuthError as e:
    print(f"Проблема с аутентификацией: {e}")
    # Необходимо заново получить токены
```

---

## RuntimeError — сессия не открыта

Если вы забыли открыть сессию:

```python
# Неправильно
client = CloudTipsClient(auth)
await client.get_me()  # RuntimeError: Сессия не открыта

# Правильно
async with CloudTipsClient(auth) as client:
    await client.get_me()
```

---

## Полный пример обработки ошибок

```python
from cloudtips import CloudTipsAuth, CloudTipsClient, CloudTipsAuthError, CloudTipsAPIError

try:
    async with CloudTipsClient(auth) as client:
        donations = await client.get_all_donations()
        cards     = await client.get_cards()
        summary   = await client.get_accumulation_summary()
except CloudTipsAuthError as e:
    print(f"Ошибка токена: {e}")
    print("Необходимо заново получить токены из браузера.")
except CloudTipsAPIError as e:
    print(f"Ошибка API {e.status_code}: {e.detail}")
except Exception as e:
    print(f"Непредвиденная ошибка: {e}")
```
