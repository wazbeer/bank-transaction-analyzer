import json
import logging
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(exist_ok=True)

log_path = LOG_DIR / "utils.log"
utils_logger = logging.getLogger(__name__)

file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
utils_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler.setFormatter(formatter)
utils_logger.addHandler(file_handler)
utils_logger.propagate = False

def excel_reader(excel_path: str) -> list[dict]:
    """Принимает на вход путь к xlsx файлу транзакций и возвращает список словарей"""
    utils_logger.info(f"Excel file read attempt from {excel_path}")
    try:
        df = pd.read_excel(excel_path)
        df = df.fillna("")
        result = df.to_dict(orient="records")
        utils_logger.info("Excel file read success")
        return result
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        utils_logger.error(f"Error at {excel_path}, error: {e}")
        return []


def load_user_settings(settings_path: str) -> dict:
    """Принимает путь до JSON файла с настройками пользователя и возращает словарь"""
    utils_logger.info(f"User settings acquiring attempt from '{settings_path}'")
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            utils_logger.info(f"Loaded JSON from '{settings_path}'")

        if isinstance(data, dict):
            utils_logger.info(f"Successfully acquired user settings from '{settings_path}'")
            return data

        utils_logger.error(f"'{settings_path}' is not a dict")
        return {"user_currencies": [], "user_stocks": []}

    except (FileNotFoundError, json.JSONDecodeError) as e:
        utils_logger.error(f"Error handling file '{settings_path}': {e}")
        return {}


def get_currency_rates(currency_list: list[str]) -> list[dict]:
    """принимает список словарей с валютами и возвращает список словарей с названием валюты и курсом обмена"""
    utils_logger.info(f"Currency rates acquiring attempt from '{currency_list}'")
    try:
        result_list = []
        payload: dict = {}
        headers: dict = {
            "apikey": os.getenv("API_KEY"),
        }
        for i in currency_list:
            url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={i}&amount=1"

            response = requests.request("GET", url, headers=headers, data=payload)

            data = response.json()

            var = {"currency": i, "rate": round(float(data["result"]), 2)}
            result_list.append(var)
        utils_logger.info(f"Successfully acquired currency rates from '{currency_list}' as {result_list}")
        return result_list
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        utils_logger.error(f"Error handling file '{currency_list}': {e}")
        return []


def get_stock_prices(stock_list: list[str]) -> list[dict]:
    """Принимает список акций, возвращает список словарей с их названием стоимостью"""
    utils_logger.info(f"Stock prices acquiring attempt from '{stock_list}'")
    try:
        result_stocks = []
        apikey = os.getenv("STOCKS_API")
        for stock in stock_list:
            url = f"https://financialmodelingprep.com/api/v3/quote/{stock}?apikey={apikey}"

            response = requests.request("GET", url)
            data = response.json()
            price = round(float(data[0]["price"]), 2)
            result_stocks.append({"stock": stock, "price": price})
        utils_logger.info(f"Successfully acquired stock prices from '{stock_list}' as {result_stocks}")
        return result_stocks
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        utils_logger.error(f"Error handling file '{stock_list}': {e}")
        return [{"stock": stock, "price": 0.0}]
