from functools import wraps
from pathlib import Path
from typing import Callable, Optional
import pandas as pd
from src.views import _parse_data
from datetime import datetime, timedelta
import os

os.makedirs("reports", exist_ok=True)


def report_to_file(filename: Optional[str | Callable] = None):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
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
def spending_by_category(transactions: pd.DataFrame,category: str,date: Optional[str] = None) -> pd.DataFrame:
    if date is not None:
        tx_date = _parse_data(date)
    else:
        tx_date = datetime.now()

    start_date = tx_date - timedelta(days=90)

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)

    filtered_df = transactions[
        (transactions["Категория"] == category) &
        (transactions["Дата операции"] >= start_date) &
        (transactions["Дата операции"] <= tx_date)
        ]

    return filtered_df


