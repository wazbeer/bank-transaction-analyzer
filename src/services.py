import logging
import math
from pathlib import Path

from src.views import _parse_data

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"


LOG_DIR.mkdir(exist_ok=True)

log_path = LOG_DIR / "services.log"
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.propagate = False


def investment_bank(month: str, transactions: list[dict], limit: int) -> float:
    """Принимает строку месяца, список словарей и лимит, возвращает данные инвесткопилки"""
    logger.info("investment calculation attempt")
    total_investment = 0.0
    for transaction in transactions:
        status = transaction.get("Статус")
        if status and status != "OK":
            continue

        parsed_date = _parse_data(transaction.get("Дата операции"))
        if not parsed_date or parsed_date.strftime("%Y-%m") != month:
            continue

        amount = transaction.get("Сумма операции")

        if amount and amount < 0:
            spent = abs(float(amount))

            rounded_amount = math.ceil(spent / limit) * limit

            delta = rounded_amount - spent

            total_investment += delta

    logger.info(f"investment calculation successful, returned {round(total_investment, 2)}")
    return round(total_investment, 2)
