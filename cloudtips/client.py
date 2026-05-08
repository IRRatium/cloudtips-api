"""
Асинхронный клиент CloudTips API.
"""
import asyncio
from datetime import datetime, timezone, timedelta
from typing import AsyncIterator, Callable, List, Optional

import aiohttp

from .auth import CloudTipsAuth
from .models import AccumulationSummary, Card, Donation, PayoutFeeInfo, ReceiverProfile

_BASE_URL = "https://api.cloudtips.ru/api"
_MSK = timezone(timedelta(hours=3))

_HEADERS_BASE = {
    "Accept":          "application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Origin":          "https://lk.cloudtips.ru",
    "Referer":         "https://lk.cloudtips.ru/",
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


class CloudTipsClient:
    """
    Асинхронный клиент для работы с CloudTips API.

    Используйте как контекстный менеджер, чтобы сессия aiohttp
    корректно открывалась и закрывалась::

        async with CloudTipsClient(auth) as client:
            donations = await client.get_all_donations()

    Или управляйте сессией вручную::

        client = CloudTipsClient(auth)
        await client.open()
        try:
            donations = await client.get_all_donations()
        finally:
            await client.close()
    """

    def __init__(self, auth: CloudTipsAuth, base_url: str = _BASE_URL) -> None:
        self._auth = auth
        self._base_url = base_url.rstrip("/")
        self._session: Optional[aiohttp.ClientSession] = None

    # ------------------------------------------------------------------
    # Управление сессией
    # ------------------------------------------------------------------

    async def open(self) -> None:
        """Открыть aiohttp-сессию."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

    async def close(self) -> None:
        """Закрыть aiohttp-сессию."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> "CloudTipsClient":
        await self.open()
        return self

    async def __aexit__(self, *_) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Донаты
    # ------------------------------------------------------------------

    async def get_donations(
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

        data = await self._get("/timeline", params={
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
                "comment": (item.get("comment") or item.get("payerComment") or "").strip(),
                "date":    item.get("createdDate", now.isoformat()),
            }))
        return result

    async def get_all_donations(
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
            batch = await self.get_donations(since=since, until=until, limit=50, page=page)
            if not batch:
                break
            result.extend(batch)
            if len(batch) < 50:
                break
            page += 1
        return sorted(result, key=lambda d: d.date)

    async def poll(
        self,
        interval: int = 30,
        since: Optional[datetime] = None,
        callback: Optional[Callable[[Donation], None]] = None,
    ) -> AsyncIterator[Donation]:
        """
        Асинхронный генератор: бесконечный поллинг новых донатов.

        Использование как async-генератора::

            async for donation in client.poll(interval=15):
                print(f"Новый донат: {donation}")

        Или с async-колбэком (блокирующий режим)::

            async def handle(donation):
                await bot.send_message(chat_id, str(donation))

            await client.poll(interval=15, callback=handle)

        :param interval: пауза между запросами в секундах
        :param since: с какого момента начинать (по умолчанию — прямо сейчас)
        :param callback: если передан — метод блокируется и вызывает колбэк
        """
        last_seen_ids: set = set()
        cursor = _ensure_tz(since or datetime.now(_MSK))

        for d in await self.get_all_donations(since=cursor):
            last_seen_ids.add(d.transaction_id)

        while True:
            await asyncio.sleep(interval)

            try:
                fresh = await self.get_all_donations(since=cursor)
            except Exception as exc:
                print(f"[cloudtips] Ошибка при поллинге: {exc}")
                continue

            for donation in fresh:
                if donation.transaction_id not in last_seen_ids:
                    last_seen_ids.add(donation.transaction_id)
                    cursor = max(cursor, donation.date)
                    if callback:
                        result = callback(donation)
                        if hasattr(result, "__await__"):
                            await result
                    else:
                        yield donation

    # ------------------------------------------------------------------
    # Профиль
    # ------------------------------------------------------------------

    async def get_me(self) -> ReceiverProfile:
        """
        Получить профиль текущего пользователя.

        :return: :class:`ReceiverProfile`

        Пример::

            me = await client.get_me()
            print(me.full_name)       # Иван Иванов
            print(me.payout_method)   # Accumulation
        """
        data = await self._get("/receivers/me")
        return ReceiverProfile.from_dict(data.get("data", {}))

    # ------------------------------------------------------------------
    # Карты
    # ------------------------------------------------------------------

    async def get_cards(self) -> List[Card]:
        """
        Получить список привязанных карт.

        :return: список :class:`Card`

        Пример::

            for card in await client.get_cards():
                print(card)         # MIR *0000 (BANK, до 01/28) [по умолчанию]
                print(card.token)   # tk_...
        """
        data = await self._get("/cards")
        return [Card.from_dict(item) for item in data.get("data", [])]

    async def delete_card(self, card_token: str) -> bool:
        """
        Удалить привязанную карту.

        :param card_token: токен карты (``card.token``)
        :return: ``True`` если удаление прошло успешно
        """
        data = await self._delete("/cards", json={"cardToken": card_token})
        return data.get("succeed", False)

    # ------------------------------------------------------------------
    # Выплаты и баланс
    # ------------------------------------------------------------------

    async def get_payout_fee_info(self) -> PayoutFeeInfo:
        """
        Получить информацию о комиссиях при выводе средств.

        :return: :class:`PayoutFeeInfo`
        """
        data = await self._get("/payout/fee/info")
        return PayoutFeeInfo.from_dict(data.get("data", {}))

    async def get_accumulation_summary(self) -> AccumulationSummary:
        """
        Получить сводку по накопленным средствам (баланс к выводу).

        :return: :class:`AccumulationSummary`

        Пример::

            s = await client.get_accumulation_summary()
            print(f"Накоплено: {s.accumulated_amount}₽")
            print(f"Комиссия: {s.commission_percent}%")
        """
        data = await self._get("/accumulations/summary")
        return AccumulationSummary.from_dict(data.get("data", {}))

    async def get_payout_method(self) -> str:
        """
        Получить текущий метод выплат.

        :return: ``"Instant"`` или ``"Accumulation"``
        """
        return (await self.get_me()).payout_method

    async def set_payout_method(self, method: str = "Instant") -> bool:
        """
        Установить метод выплат.

        :param method: ``"Instant"`` (мгновенно) или ``"Accumulation"`` (накопительно)
        :return: ``True`` если успешно
        """
        data = await self._post("/receivers/payout-method", json={"payoutMethod": method})
        return data.get("succeed", False)

    # ------------------------------------------------------------------
    # Внутренние HTTP-методы
    # ------------------------------------------------------------------

    def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            raise RuntimeError(
                "Сессия не открыта. Используйте `async with CloudTipsClient(auth) as client:` "
                "или вызовите `await client.open()` перед первым запросом."
            )
        return self._session

    async def _get(self, path: str, params: Optional[dict] = None) -> dict:
        session = self._ensure_session()
        headers = {**_HEADERS_BASE, **await self._auth.headers()}
        async with session.get(
            self._base_url + path,
            headers=headers,
            params=params,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as response:
            await _raise_for_status(response)
            return await response.json()

    async def _post(self, path: str, json: Optional[dict] = None) -> dict:
        session = self._ensure_session()
        headers = {**_HEADERS_BASE, **await self._auth.headers()}
        async with session.post(
            self._base_url + path,
            headers=headers,
            json=json,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as response:
            await _raise_for_status(response)
            return await response.json()

    async def _delete(self, path: str, json: Optional[dict] = None) -> dict:
        session = self._ensure_session()
        headers = {**_HEADERS_BASE, **await self._auth.headers()}
        async with session.delete(
            self._base_url + path,
            headers=headers,
            json=json,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as response:
            await _raise_for_status(response)
            return await response.json()


class CloudTipsAPIError(Exception):
    """Ошибка запроса к CloudTips API."""

    def __init__(self, status_code: int, detail: object) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


def _ensure_tz(dt: datetime) -> datetime:
    """Добавляет МСК таймзону если её нет."""
    return dt if dt.tzinfo else dt.replace(tzinfo=_MSK)


async def _raise_for_status(response: aiohttp.ClientResponse) -> None:
    if not response.ok:
        try:
            detail = await response.json()
        except Exception:
            detail = await response.text()
        raise CloudTipsAPIError(response.status, detail)
