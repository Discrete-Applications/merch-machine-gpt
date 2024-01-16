import logging
import os
import base64

from flask import Flask, request, render_template
from flask_restful import Resource, Api
from datetime import datetime as dt
from os import getenv
from pathlib import Path

# set up the application and the api
app: Flask  = Flask(__name__)
api: Api  = Api(app)
application: Flask = app

# Set up logging
log_date: str = dt.now().strftime("%d%b%Y")
log_folder: Path = Path.cwd() / Path("logs")
if not log_folder.exists():
    log_folder.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=log_folder / f"{log_date}_merch_main.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)

# Set up the API endpoints
class getHelloWorld(Resource):
    def get(self):
        return {"message": "Hello world!"}
    
api.add_resource(getHelloWorld, "/helloworld")

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
    load_dotenv()

    # Run the application
    logging.info("Starting Merch Machine Main for debugging on localhost.")
    app.run(debug=True, host="localhost", port=5000)
