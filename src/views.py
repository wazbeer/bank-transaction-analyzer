import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from src.utils import load_user_settings, get_currency_rates, get_stock_prices, excel_reader
import json

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"


LOG_DIR.mkdir(exist_ok=True)

log_path = LOG_DIR / "views.log"
utils_logger = logging.getLogger(__name__)

file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
utils_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler.setFormatter(formatter)
utils_logger.addHandler(file_handler)

def _parse_data(data_str: str) -> None | datetime:
    formats = ["%Y-%m-%d %H:%M:%S", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y", "%Y-%m-%d"]
    if isinstance(data_str, (datetime, pd.Timestamp)):
        return data_str
    if isinstance(data_str, str):
        for fmt in formats:
            try:
                return datetime.strptime(data_str, fmt)
            except ValueError:
                continue
    return None

def _get_greetings(dt: datetime) -> str:
    if 6 <= dt.hour < 12:
        return "Доброе утро"
    elif 12 <= dt.hour < 18:
        return "Добрый день"
    elif 18 <= dt.hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

def _filter_transactions(transactions: list[dict], start_date: datetime, end_date: datetime) -> list[dict]:
    result = []
    for tx in transactions:
        if tx.get("Статус") != "OK":
            continue
        tx_date = _parse_data(tx.get("Дата операции"))
        if tx_date is not None:
            if start_date <= tx_date <= end_date:
                result.append(tx)
    return result


def main_page(data_time_str: str, data_path: str = "data/operations.xlsx", settings_path: str = "user_settings.json") -> str:
    target_date = _parse_data(data_time_str)
    if not target_date:
        target_date = datetime.now()
    greetings = _get_greetings(target_date)
    start_date = target_date.replace(day=1, hour=0, minute=0, second=0)
    all_tx = excel_reader(data_path)
    filtered_tx = _filter_transactions(all_tx, start_date, target_date)

    cards_dict = {}

    for tx in filtered_tx:
        card_raw = tx.get("Номер карты")
        amount = tx.get("Сумма операции")

        if card_raw and isinstance(amount, (int, float)) and amount < 0:
            # Берём последние 4 цифры карты
            last_digits = str(card_raw)[-4:]

            cards_dict[last_digits] = cards_dict.get(last_digits, 0.0) + abs(amount)

    cards_list = []
    for last_digits, total_spent in cards_dict.items():
        cards_list.append({
            "last_digits": last_digits,
            "total_spent": round(total_spent, 2),
            "cashback": round(total_spent // 100, 2)
        })


    top_5_raw = sorted(filtered_tx, key=lambda tx: abs(float(tx.get("Сумма платежа", 0))), reverse=True)[:5]

    top_transactions = []
    for tx in top_5_raw:
        tx_date = _parse_data(tx.get("Дата операции"))
        data_str = tx_date.strftime("%d.%m.%Y") if tx_date else ""

        top_transactions.append({
            "date": data_str,
            "amount": float(tx.get('Сумма платежа', 0)),
            "category": str(tx.get("Категория", "")),
            "description": str(tx.get("Описание", ""))
        })

    settings = load_user_settings(settings_path)

    user_currency_rates = get_currency_rates(settings.get("user_currencies",[]))
    user_stock_prices = get_stock_prices(settings.get("user_stocks",[]))


    main_result = {
        "greeting": greetings,
        "cards": cards_list,
        "top_transactions": top_transactions,
        "currency_rates": user_currency_rates,
        "stock_prices": user_stock_prices,
    }

    return json.dumps(main_result, ensure_ascii=False, indent=4)
