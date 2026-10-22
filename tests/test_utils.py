from typing import Any
from unittest.mock import patch

import pandas as pd

from src.utils import excel_reader, get_currency_rates, get_stock_prices, load_user_settings


def test_excel_reader_success(tmp_path: Any) -> None:
    file_path = tmp_path / "test.xlsx"
    df = pd.DataFrame([{"Категория": "Супермаркеты", "Сумма операции": -100}])
    df.to_excel(file_path, index=False)

    result = excel_reader(str(file_path))
    assert len(result) == 1
    assert result[0]["Категория"] == "Супермаркеты"


def test_excel_reader_not_found() -> None:
    assert excel_reader("non_existent_file.xlsx") == []


def test_load_user_settings_success(tmp_path: Any) -> None:
    file_path = tmp_path / "settings.json"
    file_path.write_text('{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}', encoding="utf-8")

    result = load_user_settings(str(file_path))
    assert result["user_currencies"] == ["USD"]


def test_load_user_settings_invalid_file() -> None:
    assert load_user_settings("invalid.json") == {}


@patch("requests.request")
def test_get_currency_rates_success(mock_request: Any) -> None:
    mock_request.return_value.json.return_value = {"result": 90.5}

    rates = get_currency_rates(["USD"])
    assert len(rates) == 1
    assert rates[0]["currency"] == "USD"
    assert rates[0]["rate"] == 90.5


@patch("requests.request")
def test_get_currency_rates_error(mock_request: Any) -> None:
    mock_request.side_effect = Exception("API error")
    assert get_currency_rates(["USD"]) == []


@patch("requests.request")
def test_get_stock_prices_success(mock_request: Any) -> None:
    mock_request.return_value.json.return_value = [{"price": 180.25}]

    stocks = get_stock_prices(["AAPL"])
    assert len(stocks) == 1
    assert stocks[0]["stock"] == "AAPL"
    assert stocks[0]["price"] == 180.25


@patch("requests.request")
def test_get_stock_prices_error(mock_request: Any) -> None:
    mock_request.side_effect = Exception("API error")
    assert get_stock_prices(["AAPL"]) == [{"stock": "AAPL", "price": 0.0}]
