from src.views import _parse_data
import datetime
import math

def investment_bank(month: str,transactions: list[dict],limit: int) -> float:
    total_investment = 0.0
    for transaction in transactions:
        if transaction.get("Статус") != "OK":
            continue

        parsed_date = _parse_data(transaction.get("Дата операции"))
        if not parsed_date or  parsed_date.strftime("%Y-%m") != month:
            continue
        amount = transaction.get("Сумма операции")
        if amount and amount < 0:
            spent = abs(float(amount))

            rounded_amount = math.ceil(spent / limit) * limit

            delta = rounded_amount - spent

            total_investment +=  delta

    return round(total_investment, 2)