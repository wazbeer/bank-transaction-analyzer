from typing import Any

import pandas as pd

from src.reports import report_to_file, spending_by_category


def test_spending_by_category() -> None:
    df = pd.DataFrame(
        [
            {"Категория": "Супермаркеты", "Дата операции": "31.12.2021 16:44:00", "Сумма операции": -100},
            {"Категория": "Фастфуд", "Дата операции": "30.12.2021 12:00:00", "Сумма операции": -50},
        ]
    )

    result = spending_by_category(df, "Супермаркеты", "2021-12-31")
    assert len(result) == 1
    assert result.iloc[0]["Категория"] == "Супермаркеты"


def test_report_to_file_custom_name(tmp_path: Any) -> None:
    target_file = tmp_path / "custom_report.json"

    @report_to_file(filename=str(target_file))
    def dummy_report() -> pd.DataFrame:
        return pd.DataFrame([{"A": 1}])

    dummy_report()
    assert target_file.exists()
