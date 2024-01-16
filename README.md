# Merch Machine Application

The Merch Machine is an application that allows users to generate merchandise using images. It provides a RESTful API for generating merchandise and includes web pages for the user interface.

## Table of Contents

- [Merch Machine Application](#merch-machine-application)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Usage](#usage)
    - [API Endpoints](#api-endpoints)
    - [Web Pages](#web-pages)
  - [Environment Variables](#environment-variables)
  - [Logging](#logging)
  - [Contributing](#contributing)
  - [License](#license)

## Prerequisites

Before running the Merch Machine application, make sure you have the following prerequisites:

- Python 3.x
- Flask (installed via pip)
- Flask-RESTful (installed via pip)
- Requests (installed via pip)
- dotenv (installed via pip)

## Setup

1. Clone the repository to your local machine.

2. Install the required dependencies using the following command:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root directory and set the necessary environment variables as described in the [Environment Variables](#environment-variables) section.

4. Ensure you have the required folder structure and files:

   ```
   - merch-machine/
     - logs/
     - merch/
     - photos/
     - local/
       - .env
   ```

5. Run the application using the following command:

   ```bash
   python merch_machine_main.py
   ```

## Usage

The Merch Machine application provides both a RESTful API and web pages for generating merchandise.

### API Endpoints

- `/helloworld`: A simple endpoint to check if the server is running.

- `/generatemerch`: A POST request to generate merchandise. Requires proper authorization and content type headers. See the API documentation for details.

### Web Pages

- `/`: The main web page for the Merch Machine application. Users can interact with the application here.

- `/privacy`: The privacy policy page for users to review.

## Environment Variables

The application relies on several environment variables for configuration. These variables can be set in a `.env` file in the `local/` directory. Here are the required environment variables:

- `OPENAI_API_KEY`: The API key for authenticating with OpenAI (for authorization).

- `TEST_API_KEY`: A test API key for testing purposes.

- `TEEMILL_PUBLIC_TOKEN`: The public token for authenticating with Teemill (for authorization).

## Logging

The application uses the Python `logging` module to log various events and errors. Log files are stored in the `logs/` directory. Make sure to configure logging according to your needs, including the log file location, log level, and log format.

## Contributing

Contributions to the Merch Machine application are welcome. If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request. Reach out directly to merch_machine@discreteapplications.com

## License

This project is licensed under the [MIT License](LICENSE).