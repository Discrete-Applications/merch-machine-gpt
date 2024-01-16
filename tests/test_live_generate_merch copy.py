import random
import requests
import logging
import json

from pathlib import Path
from dotenv import load_dotenv
from os import getenv
from datetime import datetime as dt

today: str = dt.today().strftime("%Y-%m-%d")
logging.basicConfig(
    filename=Path.cwd() / f"logs/{today}_test_generate_merch.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv(Path.cwd() / "local/.env")
test_key: str = getenv("TEST_API_KEY")

image_url: str = "https://wonderfulengineering.com/wp-content/uploads/2014/10/image-wallpaper-15-1024x768.jpg"
post_url: str = "https://merchmachine.discreteapplications.com/generatemerch"

headers = {
    "Content-Type": "application/json",
    "Authorization": test_key,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
}

item_codes: list[str] = [code for code in json.load(open(Path.cwd() / "lookup_data/price_list.json", "r"))]
data: list[dict] = json.load(open(Path.cwd() / "lookup_data/available_options.json", "r"))["data"]
color_options: dict = dict()

for item in range(len(data)):
    color_options[data[item]["item_code"]] = data[item]["colours"]

test_codes: list = random.choices(item_codes, k=5)

logging.debug(f"Test started at {dt.now()}")

for code in test_codes:

    colors: str = ','.join(random.choices([col for col in color_options[code]], k=3 if len(color_options[code]) >= 3 else 1))

    payload = {
        "name": "Test Merch",
        "description": "This is a test merch.",
        "image_url": image_url,
        "price": "0.00",
        "colours": colors,
        "item_code": code,
    }

    logging.debug(f"Testing with payload: {payload}")

    results = requests.post(post_url, headers=headers, json=payload)
    
    try:
        logging.debug(f"Test results: {results.json()['name']} - {results.json()['url']}")
    except Exception as e:
        logging.debug(f"An error occured {e}")
        logging.debug(f"data returned: {results.content}")

logging.debug(f"Test completed at {dt.now()}")