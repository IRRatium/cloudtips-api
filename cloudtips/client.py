"""
Клиент CloudTips API.
"""
import time
from datetime import datetime, timezone
from typing import Callable, Iterator, List, Optional

import requests

from .auth import CloudTipsAuth
from .models import Donation

_BASE_URL = "https://api.cloudtips.ru"


class CloudTipsClient:
    """
    Основной клиент для работы с CloudTips API.

    Пример быстрого старта::

        from cloudtips import CloudTipsClient, CloudTipsAuth

        auth = CloudTipsAuth(
            token="...",
            refresh_token="...",
            expires_at=1776099728.0,
            on_token_refresh=lambda td: print("Новый токен:", td.access_token),
        )
        client = CloudTipsClient(auth)

        # Получить все донаты
        donations = client.get_donations()

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
        limit: int = 100,
        page: int = 1,
    ) -> List[Donation]:
        """
        Получить список донатов.

        :param since: фильтр — только донаты после этого момента
        :param limit: кол-во на страницу (max обычно 100)
        :param page: номер страницы
        :return: список :class:`Donation`
        """
        params: dict = {"pageSize": limit, "page": page}
        if since is not None:
            params["from"] = since.isoformat()

        data = self._get("/api/payments", params=params)

        items = data if isinstance(data, list) else data.get("items", data.get("payments", []))
        return [Donation.from_dict(item) for item in items]

    def get_all_donations(self, since: Optional[datetime] = None) -> List[Donation]:
        """
        Получить все донаты с автопагинацией.

        :param since: фильтр по дате
        :return: полный список :class:`Donation`
        """
        result: List[Donation] = []
        page = 1
        while True:
            batch = self.get_donations(since=since, limit=100, page=page)
            if not batch:
                break
            result.extend(batch)
            if len(batch) < 100:
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
        :param since: с какого момента начинать (по умолчанию — «прямо сейчас»)
        :param callback: если передан — метод блокируется и вызывает колбэк
        """
        last_seen_ids: set = set()
        cursor = since or datetime.now(tz=timezone.utc)

        # Первый запрос — грузим уже известные, не отдаём как "новые"
        for d in self.get_all_donations(since=cursor):
            last_seen_ids.add(d.transaction_id)

        while True:
            time.sleep(interval)

            try:
                fresh = self.get_all_donations(since=cursor)
            except Exception as exc:
                # Не падаем, просто пробуем снова на следующей итерации
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
        url = self._base_url + path
        response = self._session.get(
            url,
            headers=self._auth.headers(),
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


def _raise_for_status(response: requests.Response) -> None:
    if not response.ok:
        try:
            detail = response.json()
        except Exception:
            detail = response.text
        raise CloudTipsAPIError(response.status_code, detail)
