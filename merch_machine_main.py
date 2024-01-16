import logging
import os
import base64
import requests
import json

from flask import Flask, request, render_template
from flask_restful import Resource, Api
from datetime import datetime as dt
from os import getenv
from pathlib import Path

# global variables
date: str = dt.now().strftime("%d%b%Y")
price_list: dict = json.load(open(Path.cwd() / "lookup_data/price_list.json", "r"))

# build folders if they do not exist
log_folder: Path = Path.cwd() / Path("logs")
if not log_folder.exists():
    log_folder.mkdir(parents=True, exist_ok=True)

merch_folder: Path = Path.cwd() / Path("merch")
if not merch_folder.exists():
    merch_folder.mkdir(parents=True, exist_ok=True)

photos_folder: Path = Path.cwd() / Path("photos")
if not photos_folder.exists():
    photos_folder.mkdir(parents=True, exist_ok=True)

# Set up logging
logging.basicConfig(
    filename=log_folder / f"{date}_merch_main.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)

# set up the application and the api
app: Flask = Flask(__name__)
api: Api = Api(app)
application: Flask = app


# Set up the API endpoints
class getHelloWorld(Resource):
    def get(self):
        return {"message": "Hello world!"}


class generateMerch(Resource):
    def post(self):
        openai_api_key: str = getenv("OPENAI_API_KEY")
        test_api_key: str = getenv("TEST_API_KEY")

        if (
            request.headers.get("Authorization") != openai_api_key
            and request.headers.get("Authorization") != test_api_key
        ):
            if app.debug:
                logging.warning(
                    (f"Invalid authorization key: {request.headers.get('Authorization')}",
                    f"expected {test_api_key} or {openai_api_key}")
                )
            return {"message": "Invalid authorization key."}, 401

        if request.headers.get("Content-Type") != "application/json":
            return {
                "message": (
                    "Invalid content type. Expected application/json got ",
                    f"{request.headers.get('Content-Type')}",
                )
            }, 400

        logging.info(
            f"Received request to generate merch from {'OpenAI' if request.headers.get('Authorization') == openai_api_key else 'Test'} client."
        )

        # get the request data
        data = request.get_json()
        logging.debug(f"Received request data: {data}")

        # get the image data
        merch_image_url: str = data["image_url"]
        result: str = self.process_image(merch_image_url)
        print(result[:10])
        if result == "http_request_error" or result == "invalid_url_error":
            return {
                "message": "Error occurred during HTTP request.",
                "remedy": (
                    "Regenerate the same image, then ask the user to right click ",
                    "the image and select 'Copy Image Link', then paste that link into the chat.",
                ),
            }, 500
        elif result == "unexpected_error":
            return {
                "message": "An unexpected error occurred.",
                "remedy": (
                    "Try again. If the error persists, contact the developer at ",
                    "merchmachine@discreteapplications.com.",
                ),
            }, 500
        else:
            merch_image_b64: str = result

        # get the data from the request
        try:
            merch_name: str = data["name"]
        except KeyError:
            merch_name: str = "No name provided"
        try:
            merch_description: str = data["description"]
        except KeyError:
            merch_description: str = "No description provided, contact the dev merch_machine@discreteapplications.com"
        try:
            merch_colours: str = data["colours"]
        except KeyError:
            merch_colours: str = "White"
        merch_cross_sell: bool = True

        # validate and update the price
        merch_item_code: str = data["item_code"]
        merch_price: str = data["price"]
        validated_price: tuple = self.validate_price(
            merch_price, merch_item_code, price_list
        )
        if not validated_price[0]:
            logging.error("Invalid price or item code.")
            merch_validated_price: str = "0.00"
        else:
            merch_validated_price: str = str(validated_price[1])

        final_product = self.get_product(
            {
                "image_url": merch_image_b64,
                "name": merch_name,
                "description": merch_description,
                "price": merch_validated_price,
                "colours": merch_colours,
                "item_code": merch_item_code,
                "cross_sell": merch_cross_sell,
            }
        )

        # return the data to the user
        return final_product

    def process_image(self, image_url: str) -> str:
        """
        Process an image from the given URL and return a Base64 encoded string.

        Args:
        - image_url (str): The URL of the image to be processed.

        Returns:
        - str: A Base64 encoded string representation of the processed image, or an error code if there are any issues.
        """
        try:
            # Validate the URL
            if not image_url.startswith("http://") and not image_url.startswith(
                "https://"
            ):
                raise ValueError("Invalid URL format")

            # Fetch the image data
            image_data: bytes = requests.get(image_url).content

            # Extract image name from URL
            image_name: str = f"{image_url.split('/')[-1].split('.')[0]}.txt"

            # Decode the image data as a Base64 string
            b64_image_str: str = "data:image/png;base64," + base64.b64encode(
                image_data
            ).decode("utf-8")

            # Create a file path for saving the image data
            image_path: Path = Path.cwd() / "photos" / f"{image_name}"

            # Save the image data to a text file
            with open(image_path, "w") as f:
                f.write(b64_image_str)

            return b64_image_str

        except requests.exceptions.RequestException as e:
            logging.error(f"Error during HTTP request: {e}")
            return "http_request_error"
        except ValueError as e:
            logging.error(f"Invalid URL format: {e}")
            return "invalid_url_error"
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return "unexpected_error"

    def validate_price(self, price_str: str, item_code: str, price_list: dict) -> tuple:
        """
        Validate the given price against the price list.

        Args:
        - price_str (str): The price to be validated.
        - item_code (str): The item code for which the price is being validated.
        - price_list (dict): A dictionary containing item codes as keys and corresponding prices as values.

        Returns:
        - tuple: A tuple containing a boolean indicating validation success and the validated price.
        """
        try:
            price = float(price_str)
            if item_code in price_list:
                item_price = float(price_list[item_code])
                validated_price = round(price + item_price + 5.00, ndigits=2)
                return True, validated_price
            else:
                return False, None
        except ValueError as e:
            logging.error(f"Invalid price format: {e}")
            return False, None
        except KeyError as e:
            logging.error(f"Item code not found in price list: {e}")
            return False, None
        except Exception as e:
            logging.error(f"An unexpected error occurred in validate_price: {e}")
            return False, None

    def get_product(self, options: dict[str, str]) -> dict[str, str]:
        """
        Send a POST request to Teemill to create a product.

        Args:
        - options (dict[str, str]): Product creation options.

        Returns:
        - dict[str, str] or None: Response from Teemill or None on error.

        This function sends a POST request to Teemill to create a product using the provided options.
        It handles potential errors gracefully and returns the response if successful.
        """
        public_teemill_token: str = getenv("TEEMILL_PUBLIC_TOKEN")
        teemill_create_endpoint: str = "https://teemill.com/omnis/v3/product/create"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/html",
            "Authorization": public_teemill_token,
        }
        try:
            response = requests.post(
                teemill_create_endpoint, headers=headers, json=options
            )
            response.raise_for_status()
            logging.debug(f"Response from POST request to Teemill: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.critical(f"Request to Teemill failed: {e}")
            return {
                "message": "Error occurred during request to TeeMill.",
                "remedy": (
                    "Regenerate the same image, then ask the user to right click ",
                    "the image and select 'Copy Image Link', then paste that link into the chat.",
                ),
            }, 500
        except Exception as e:
            logging.critical(f"Error occurred while getting product: {e}")
            return {
                "message": "An unexpected error occurred.",
                "remedy": (
                    "Regenerate the same image, then ask the user to right click ",
                    "the image and select 'Copy Image Link', then paste that link into the chat.",
                    "If the issue persists, contact the dev at merchmachine@discreteapplications.com.",
                ),
            }, 500


api.add_resource(getHelloWorld, "/helloworld")
api.add_resource(generateMerch, "/generatemerch")


# Set up the web pages
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy_policy.html")


if __name__ == "__main__":
    # load local environment variables
    local_vars_path: Path = Path.cwd() / "local/.env"
    from dotenv import load_dotenv

    load_dotenv(Path.cwd() / "local/.env")

    # Run the application
    logging.info("Starting Merch Machine Main for debugging on localhost.")
    try:
        app.run(debug=True, host="localhost", port=5000)
    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}")