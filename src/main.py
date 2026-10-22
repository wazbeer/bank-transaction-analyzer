import pandas as pd
from src.reports import spending_by_category
from src.services import investment_bank
from src.utils import excel_reader
from src.views import main_page


def main() -> None:
    print("=== 1. Генерация главной страницы (JSON) ===")
    print(main_page("2021-12-31 16:44:00"))

    print("\n=== 2. Расчет Инвесткопилки ===")
    transactions = excel_reader("data/operations.xlsx")
    print(investment_bank("2021-12", transactions, 50))

    print("\n=== 3. Формирование отчета 'Траты по категории' ===")
    df = pd.read_excel("data/operations.xlsx")
    spending_by_category(df, "Супермаркеты", "2021-12-31")


if __name__ == "__main__":
    main()