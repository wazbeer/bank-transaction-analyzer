from pathlib import Path
import pandas as pd
from src.reports import spending_by_category
from src.services import investment_bank
from src.utils import excel_reader
from src.views import main_page

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = str(BASE_DIR / "data" / "operations.xlsx")
SETTINGS_PATH = str(BASE_DIR / "user_settings.json")

def main() -> None:
    print("=== 1. Генерация главной страницы (JSON) ===")
    print(main_page("2021-12-31 16:44:00", data_path=DATA_PATH, settings_path=SETTINGS_PATH))

    print("\n=== 2. Расчет Инвесткопилки ===")
    transactions = excel_reader(DATA_PATH)
    print(investment_bank("2021-12", transactions, 50))

    print("\n=== 3. Формирование отчета 'Траты по категории' ===")
    df = pd.read_excel(DATA_PATH)
    report_df = spending_by_category(df, "Супермаркеты", "2021-12-31")
    print(report_df[["Дата операции", "Категория", "Сумма операции", "Описание"]].head())


if __name__ == "__main__":
    main()