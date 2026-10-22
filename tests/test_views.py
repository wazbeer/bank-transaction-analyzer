import json
from datetime import datetime
from typing import Any
from unittest.mock import patch

from src.views import _filter_transactions, _get_greetings, _parse_data, main_page


def test_parse_data_valid() -> None:
    dt = _parse_data("2021-12-31 16:44:00")
    assert isinstance(dt, datetime)
    assert dt.year == 2021


def test_parse_data_invalid() -> None:
    assert _parse_data("invalid_date") is None


def test_get_greetings() -> None:
    assert _get_greetings(datetime(2021, 12, 31, 8, 0)) == "Доброе утро"
    assert _get_greetings(datetime(2021, 12, 31, 14, 0)) == "Добрый день"
    assert _get_greetings(datetime(2021, 12, 31, 19, 0)) == "Добрый вечер"
    assert _get_greetings(datetime(2021, 12, 31, 2, 0)) == "Доброй ночи"


def test_filter_transactions() -> None:
    txs = [
        {"Статус": "OK", "Дата операции": "31.12.2021 16:44:00"},
        {"Статус": "FAILED", "Дата операции": "31.12.2021 16:44:00"},
        {"Статус": "OK", "Дата операции": "01.01.2020 10:00:00"},
    ]
    start = datetime(2021, 12, 1)
    end = datetime(2021, 12, 31, 23, 59)
    filtered = _filter_transactions(txs, start, end)
    assert len(filtered) == 1


@patch("src.views.excel_reader")
@patch("src.views.load_user_settings")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
def test_main_page(mock_stocks: Any, mock_rates: Any, mock_settings: Any, mock_excel: Any) -> None:
    mock_excel.return_value = [
        {
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -160.89,
            "Сумма платежа": -160.89,
            "Дата операции": "31.12.2021 16:44:00",
            "Категория": "Супермаркеты",
            "Описание": "Колхоз",
        }
    ]
    mock_settings.return_value = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    mock_rates.return_value = [{"currency": "USD", "rate": 90.0}]
    mock_stocks.return_value = [{"stock": "AAPL", "price": 180.0}]

    response = main_page("2021-12-31 16:44:00")
    data = json.loads(response)

    assert "greeting" in data
    assert len(data["cards"]) == 1
    assert data["cards"][0]["last_digits"] == "7197"
    assert len(data["top_transactions"]) == 1
