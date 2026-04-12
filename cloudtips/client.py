"""
Клиент CloudTips API.
"""
import time
from datetime import datetime, timezone, timedelta
from typing import Callable, Iterator, List, Optional

import requests

from .auth import CloudTipsAuth
from .models import Donation

_BASE_URL = "https://api.cloudtips.ru/api"
_MSK = timezone(timedelta(hours=3))

HEADERS_BASE = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Origin": "https://lk.cloudtips.ru",
    "Referer": "https://lk.cloudtips.ru/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


class CloudTipsClient:
    """
    Основной клиент для работы с CloudTips API.

    Пример быстрого старта::

        from cloudtips import CloudTipsClient, CloudTipsAuth

        auth = CloudTipsAuth(
            token="...",
            refresh_token="...",
            expires_at=1776099728.0,
            on_token_refresh=lambda td: print("Новый refresh:", td.refresh_token),
        )
        client = CloudTipsClient(auth)

        # Получить донаты за последние 30 дней
        donations = client.get_all_donations(since=datetime.now() - timedelta(days=30))

        # Поллинг новых донатов каждые 30 секунд
        for donation in client.poll(interval=30):
            print(donation)
    """

    def __init__(self, auth: CloudTipsAuth, base_url: str = _BASE_URL) -> None:
        self._auth = auth
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()

    # ------------------------------------------------------------------
    # Основные методы
    # ------------------------------------------------------------------

    def get_donations(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 50,
        page: int = 1,
    ) -> List[Donation]:
        """
        Получить донаты за период через /timeline.

        :param since: начало периода (по умолчанию — 24 часа назад)
        :param until: конец периода (по умолчанию — сейчас)
        :param limit: кол-во на страницу
        :param page: номер страницы
        :return: список :class:`Donation`
        """
        now       = datetime.now(_MSK)
        date_from = _ensure_tz(since or (now - timedelta(hours=24)))
        date_to   = _ensure_tz(until or now)

        data = self._get("/timeline", params={
            "page":     page,
            "limit":    limit,
            "dateFrom": date_from.isoformat(),
            "dateTo":   date_to.isoformat(),
        })

        raw_items = data.get("data", {}).get("items", [])
        result = []
        for item in raw_items:
            if item.get("operationType") != "Transaction":
                continue
            result.append(Donation.from_dict({
                "transaction_id": item.get("transactionId", 0),
                "name":    (item.get("payerName") or "Аноним").strip(),
                "amount":  int(item.get("paymentAmount", 0)),
                "tg_id":   0,
                "comment": (item.get("comment") or item.get("payerComment") or "").strip(),
                "date":    item.get("createdDate", now.isoformat()),
            }))
        return result

    def get_all_donations(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> List[Donation]:
        """
        Получить все донаты за период с автопагинацией.

        :param since: начало периода
        :param until: конец периода
        :return: полный список :class:`Donation`, отсортированный по дате
        """
        result: List[Donation] = []
        page = 1
        while True:
            batch = self.get_donations(since=since, until=until, limit=50, page=page)
            if not batch:
                break
            result.extend(batch)
            if len(batch) < 50:
                break
            page += 1
        return sorted(result, key=lambda d: d.date)

    def poll(
        self,
        interval: int = 30,
        since: Optional[datetime] = None,
        callback: Optional[Callable[[Donation], None]] = None,
    ) -> Iterator[Donation]:
        """
        Генератор: бесконечный поллинг новых донатов.

        Каждые ``interval`` секунд опрашивает API и отдаёт только **новые**
        донаты (те, что появились после последнего запроса).

        Использование как генератора::

            for donation in client.poll(interval=15):
                print(f"Новый донат: {donation}")

        Или с колбэком (блокирующий режим)::

            client.poll(interval=15, callback=handle_donation)

        :param interval: пауза между запросами в секундах
        :param since: с какого момента начинать (по умолчанию — прямо сейчас)
        :param callback: если передан — метод блокируется и вызывает колбэк
        """
        last_seen_ids: set = set()
        cursor = _ensure_tz(since or datetime.now(_MSK))

        # Первый запрос — запоминаем уже существующие, не отдаём как «новые»
        for d in self.get_all_donations(since=cursor):
            last_seen_ids.add(d.transaction_id)

        while True:
            time.sleep(interval)

            try:
                fresh = self.get_all_donations(since=cursor)
            except Exception as exc:
                # Не падаем при временных ошибках, пробуем снова
                print(f"[cloudtips] Ошибка при поллинге: {exc}")
                continue

            for donation in fresh:
                if donation.transaction_id not in last_seen_ids:
                    last_seen_ids.add(donation.transaction_id)
                    cursor = max(cursor, donation.date)
                    if callback:
                        callback(donation)
                    else:
                        yield donation

    # ------------------------------------------------------------------
    # Вспомогательные
    # ------------------------------------------------------------------

    def _get(self, path: str, params: Optional[dict] = None) -> dict:
        headers = {**HEADERS_BASE, **self._auth.headers()}
        response = self._session.get(
            self._base_url + path,
            headers=headers,
            params=params,
            timeout=15,
        )
        _raise_for_status(response)
        return response.json()


class CloudTipsAPIError(Exception):
    """Ошибка запроса к CloudTips API."""

    def __init__(self, status_code: int, detail: object) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


def _ensure_tz(dt: datetime) -> datetime:
    """Добавляет МСК таймзону если её нет."""
    return dt if dt.tzinfo else dt.replace(tzinfo=_MSK)


def _raise_for_status(response: requests.Response) -> None:
    if not response.ok:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise CloudTipsAPIError(response.status_code, detail)
