import logging
import os
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd

from src.views import _parse_data

os.makedirs("reports", exist_ok=True)

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"


LOG_DIR.mkdir(exist_ok=True)

log_path = LOG_DIR / "reports.log"
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.propagate = False


def report_to_file(filename: Optional[str | Callable] = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            if not filename or callable(filename):
                target_file = "reports/report.json"
            else:
                target_file = str(filename)

            Path(target_file).parent.mkdir(parents=True, exist_ok=True)

            if isinstance(result, pd.DataFrame):
                result.to_json(target_file, orient="records", force_ascii=False, indent=4)

            return result

        return wrapper

    if callable(filename):
        return decorator(filename)

    return decorator


@report_to_file
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Принимает Дата фрейм с транзакциями, строку с категорией и опционально строку с датой,
     возвращает отфильтрованный по категориям дата фрейм"""
    logger.info("spending by category filter attempt")
    if date is not None:
        parsed = _parse_data(date)
        tx_date = parsed if parsed is not None else datetime.now()
    else:
        tx_date = datetime.now()

    start_date = tx_date - pd.DateOffset(months=3)
    logger.info("got start date")

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    logger.info("got operation date")

    filtered_df = transactions[
        (transactions["Категория"] == category)
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= tx_date)
        & (transactions["Сумма операции"] < 0)
    ]

    logger.info("successfully filtered by category")
    return filtered_df
