from src.services import investment_bank


def test_investment_bank_success() -> None:
    transactions = [
        {"Статус": "OK", "Дата операции": "31.12.2021 16:44:00", "Сумма операции": -160.89},
        {"Статус": "OK", "Дата операции": "31.12.2021 15:00:00", "Сумма операции": -64.00},
        {"Статус": "FAILED", "Дата операции": "31.12.2021 12:00:00", "Сумма операции": -100.00},
    ]
    # Для 160.89 до 50 -> 200 (разница 39.11)
    # Для 64.00 до 50 -> 100 (разница 36.00)
    # Итого: 39.11 + 36.00 = 75.11
    result = investment_bank("2021-12", transactions, limit=50)
    assert result == 75.11


def test_investment_bank_empty() -> None:
    assert investment_bank("2021-12", [], limit=50) == 0.0
