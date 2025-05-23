# Cryptocurrency Trend Analyzer with LLM

## Description

This application fetches historical cryptocurrency K-line (candlestick) data from Binance and utilizes a Large Language Model (LLM) to perform trend analysis on the data. Users can interact with the application via a Command Line Interface (CLI) to specify the cryptocurrency, interval, and their LLM API credentials.

## Features

*   **Command Line Interface (CLI):** Easy-to-use interface for interacting with the application.
*   **Binance Data Integration:** Fetches historical K-line data directly from Binance.
*   **Configurable LLM:** Supports using different LLM API endpoints and keys (defaults to OpenAI's API structure).
*   **Docker Support:** Includes a `Dockerfile` for building and running the application in a containerized environment.
*   **Unit Tests:** Basic unit tests are provided to ensure core functionality.

## Project Structure

*   `app.py`: The main application script containing the CLI, data fetching, LLM interaction, and analysis logic.
*   `test_app.py`: Contains unit tests for the application.
*   `Dockerfile`: Defines the Docker image for containerizing the application.
*   `requirements.txt`: Lists the Python dependencies for the project.
*   `README.md`: This file, providing information about the project.

## Prerequisites

*   Python 3.9+ (developed and tested with Python 3.10)
*   Docker (optional, if you plan to use the Dockerized version)

## Setup & Installation

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application (CLI)

1.  **Run the application using:**
    ```bash
    python app.py
    ```

2.  **You will be prompted for the following information:**
    *   **Cryptocurrency Symbol:** The trading pair you want to analyze (e.g., `BTCUSDT`, `ETHUSDT`).
    *   **K-line Interval:** The time interval for the candlesticks (e.g., `1h`, `4h`, `1d`, `1w`). Refer to Binance API documentation or `python-binance` library for all valid intervals (e.g., `Client.KLINE_INTERVAL_1HOUR`).
    *   **LLM API Key:** Your API key for the chosen LLM service. **This is sensitive information and should be kept confidential.** The input will be hidden if `getpass` is available in your environment.
    *   **LLM API URL (Optional):** If you are using a custom LLM endpoint (e.g., a self-hosted model or a different provider compatible with OpenAI's API structure), you can enter it here. Press Enter to use the default (`https://api.openai.com/v1/chat/completions`).

## Building and Running with Docker

1.  **Build the Docker image:**
    From the project root directory (where the `Dockerfile` is located):
    ```bash
    docker build -t crypto-analyzer .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -it crypto-analyzer
    ```
    *   The `-it` flag is important as it runs the container in interactive mode and allocates a pseudo-TTY, which is necessary for the CLI prompts.

## Running Tests

To run the unit tests, execute the following command from the project root directory:
```bash
python -m unittest test_app.py
```

## LLM Configuration

*   **API Key:** You must provide your own API key for a compatible LLM service (e.g., OpenAI). The application prompts for this key when run.
*   **API URL:** The application defaults to using OpenAI's chat completions API endpoint (`https://api.openai.com/v1/chat/completions`), which is defined as `DEFAULT_LLM_API_URL` in `app.py`. You can override this by providing a custom URL when prompted by the CLI if you are using a different compatible LLM service or a proxy.
*   **Model:** The default model used in the LLM prompt is `gpt-3.5-turbo`. This can be changed directly in the `analyze_with_llm` function in `app.py` if needed.

## Known Limitations

*   **Binance API Restrictions:** The Binance API may have usage restrictions, including rate limits or geo-restrictions (blocking requests from certain geographical locations). The application might not function correctly if run from a restricted IP address.
*   **LLM Analysis Quality:** The quality and accuracy of the trend analysis heavily depend on the capabilities of the chosen LLM, the quality of the prompt, and the data provided. The analysis should not be considered financial advice.
*   **Error Handling:** The application includes basic error handling for API calls and user inputs. However, it can be further expanded for more complex scenarios and edge cases.
*   **Data Volume for LLM:** Very long K-line data series are truncated before being sent to the LLM to keep prompts within reasonable limits. This might affect the analysis if critical data points are omitted.

---
This README provides a comprehensive guide for users and developers of the Cryptocurrency Trend Analyzer.
