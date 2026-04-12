"""
Клиент CloudTips API.
"""
import time
from datetime import datetime, timezone, timedelta
from typing import Callable, Iterator, List, Optional

import requests

from .auth import CloudTipsAuth
from .models import Donation, Card, PayoutFeeInfo, AccumulationSummary, ReceiverProfile

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

        donations = client.get_all_donations()
        cards = client.get_cards()
        summary = client.get_accumulation_summary()
    """

    def __init__(self, auth: CloudTipsAuth, base_url: str = _BASE_URL) -> None:
        self._auth = auth
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()

    # ------------------------------------------------------------------
    # Донаты
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

        for d in self.get_all_donations(since=cursor):
            last_seen_ids.add(d.transaction_id)

        while True:
            time.sleep(interval)

            try:
                fresh = self.get_all_donations(since=cursor)
            except Exception as exc:
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
    # Профиль
    # ------------------------------------------------------------------

    def get_me(self) -> ReceiverProfile:
        """
        Получить профиль текущего пользователя.

        Содержит имя, телефон, метод выплат, лимиты сумм и другие данные.

        :return: :class:`ReceiverProfile`

        Пример::

            me = client.get_me()
            print(me.full_name)       # IRRing
            print(me.payout_method)   # Accumulation
            print(me.available_amount_min, me.available_amount_max)  # 49.0 3000.0
        """
        data = self._get("/receivers/me")
        return ReceiverProfile.from_dict(data.get("data", {}))

    # ------------------------------------------------------------------
    # Карты
    # ------------------------------------------------------------------

    def get_cards(self) -> List[Card]:
        """
        Получить список привязанных карт.

        :return: список :class:`Card`

        Пример::

            for card in client.get_cards():
                print(card)         # MIR *3742 (T-BANK (TINKOFF), до 08/34) [по умолчанию]
                print(card.token)   # tk_89e6b3c6827afd4e9ccc36db2d22f
        """
        data = self._get("/cards")
        return [Card.from_dict(item) for item in data.get("data", [])]

    def delete_card(self, card_token: str) -> bool:
        """
        Удалить привязанную карту.

        :param card_token: токен карты (``card.token``)
        :return: ``True`` если удаление прошло успешно

        Пример::

            for card in client.get_cards():
                client.delete_card(card.token)
        """
        data = self._delete("/cards", json={"cardToken": card_token})
        return data.get("succeed", False)

    # ------------------------------------------------------------------
    # Выплаты и баланс
    # ------------------------------------------------------------------

    def get_payout_fee_info(self) -> PayoutFeeInfo:
        """
        Получить информацию о комиссиях при выводе средств.

        :return: :class:`PayoutFeeInfo`

        Пример::

            fee = client.get_payout_fee_info()
            print(fee.text)
            # Стоимость вывода денег на карты Т-Банка — 5%
            # Стоимость вывода денег на карты других банков — 7%*
        """
        data = self._get("/payout/fee/info")
        return PayoutFeeInfo.from_dict(data.get("data", {}))

    def get_accumulation_summary(self) -> AccumulationSummary:
        """
        Получить сводку по накопленным средствам (баланс к выводу).

        :return: :class:`AccumulationSummary`

        Пример::

            s = client.get_accumulation_summary()
            print(f"Накоплено: {s.accumulated_amount}₽")
            print(f"Комиссия: {s.commission_percent}%")
            print(f"Следующая выплата: {s.next_payout_date or 'не запланирована'}")
        """
        data = self._get("/accumulations/summary")
        return AccumulationSummary.from_dict(data.get("data", {}))

    def get_payout_method(self) -> str:
        """
        Получить текущий метод выплат.

        :return: ``"Instant"`` или ``"Accumulation"``
        """
        return self.get_me().payout_method

    def set_payout_method(self, method: str = "Instant") -> bool:
        """
        Установить метод выплат.

        :param method: ``"Instant"`` (мгновенно) или ``"Accumulation"`` (накопительно)
        :return: ``True`` если успешно
        """
        data = self._post("/receivers/payout-method", json={"payoutMethod": method})
        return data.get("succeed", False)

    # ------------------------------------------------------------------
    # Внутренние HTTP-методы
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

    def _post(self, path: str, json: Optional[dict] = None) -> dict:
        headers = {**HEADERS_BASE, **self._auth.headers()}
        response = self._session.post(
            self._base_url + path,
            headers=headers,
            json=json,
            timeout=15,
        )
        _raise_for_status(response)
        return response.json()

    def _delete(self, path: str, json: Optional[dict] = None) -> dict:
        headers = {**HEADERS_BASE, **self._auth.headers()}
        response = self._session.delete(
            self._base_url + path,
            headers=headers,
            json=json,
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
