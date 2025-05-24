For the Chinese version, please see [README_zh.md](README_zh.md)


# Cryptocurrency Trend Analyzer with LLM

## Description

This application fetches historical cryptocurrency K-line (candlestick) data from Binance and utilizes a Large Language Model (LLM) to perform trend analysis on the data. Users can interact with the application via a Command Line Interface (CLI) or a Streamlit Web UI to specify the cryptocurrency, interval, and their LLM API credentials.

## Features

*   **Command Line Interface (CLI):** For users who prefer terminal-based interaction.
*   **Streamlit Web UI:** A user-friendly web interface for easier input and visualization.
*   **Binance Data Integration:** Fetches historical K-line data directly from Binance.
*   **Configurable LLM:** Supports using different LLM API endpoints and keys (defaults to OpenAI's API structure).
*   **Docker Support:** Includes a `Dockerfile` for building and running the application (both CLI and Streamlit versions) in a containerized environment.
*   **Unit Tests:** Basic unit tests are provided to ensure core functionality.

## Project Structure

*   `app.py`: The main application script containing the core data fetching, LLM interaction, and analysis logic. Also contains the CLI.
*   `streamlit_app.py`: The Streamlit Web UI application script.
*   `test_app.py`: Contains unit tests for `app.py`.
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

## Running the Application

You can run the application using either the CLI or the Streamlit Web UI.

### CLI Mode

1.  **Run the application using:**
    ```bash
    python app.py
    ```

2.  **You will be prompted for the following information:**
    *   **Cryptocurrency Symbol:** The trading pair you want to analyze (e.g., `BTCUSDT`, `ETHUSDT`).
    *   **K-line Interval:** The time interval for the candlesticks (e.g., `1h`, `4h`, `1d`, `1w`). Refer to Binance API documentation or `python-binance` library for all valid intervals (e.g., `Client.KLINE_INTERVAL_1HOUR`).
    *   **LLM API Key:** Your API key for the chosen LLM service. **This is sensitive information and should be kept confidential.** The input will be hidden if `getpass` is available in your environment.
    *   **LLM API URL (Optional):** If you are using a custom LLM endpoint (e.g., a self-hosted model or a different provider compatible with OpenAI's API structure), you can enter it here. Press Enter to use the default (`https://api.openai.com/v1/chat/completions`).

### Streamlit Web UI Mode

1.  **Run the Streamlit application using:**
    ```bash
    streamlit run streamlit_app.py
    ```
    This will typically open the application in your default web browser.

## Building and Running with Docker

The Docker container is configured to run the Streamlit Web UI by default.

1.  **Build the Docker image:**
    From the project root directory (where the `Dockerfile` is located):
    ```bash
    docker build -t crypto-analyzer .
    ```

2.  **Run the Docker container (for Streamlit Web UI):**
    ```bash
    docker run -p 8501:8501 crypto-analyzer
    ```
    *   Open your web browser and navigate to `http://localhost:8501`.
    *   The `-p 8501:8501` flag maps the container's port 8501 to your host machine's port 8501.

    If you wish to run the CLI version within Docker:
    ```bash
    docker run -it crypto-analyzer python app.py
    ```

## Running Tests

To run the unit tests for `app.py`, execute the following command from the project root directory:
```bash
python -m unittest test_app.py
```

## Manual Web UI Testing

This section outlines test cases to manually verify the Streamlit Web UI functionality.

1.  **Starting the Application:**
    *   **Test Case:** In your terminal (with the virtual environment activated and dependencies installed), run `streamlit run streamlit_app.py`.
    *   **Expected Result:** The application opens in a web browser (e.g., at `http://localhost:8501`) without any immediate errors shown in the browser or critical errors in the terminal.

2.  **Initial UI Elements:**
    *   **Test Case:** Observe the loaded page in the browser.
    *   **Expected Result:**
        *   The title "Cryptocurrency Trend Analyzer 📈" is displayed.
        *   An informational message about the app's purpose is visible.
        *   The sidebar on the left contains:
            *   A header "Input Parameters".
            *   A text input field for "Cryptocurrency Symbol" (default "BTCUSDT").
            *   A selectbox for "K-line Interval" (default "1h").
            *   A text input field for "Your LLM API Key 🔑" (password type).
            *   A text input field for "LLM API URL (optional)" (defaulting to OpenAI's URL).
        *   The "Analyze Trends 🚀" button is visible in the sidebar.
        *   The main area of the page is initially clean, ready for results or placeholders.

3.  **Valid Inputs & Successful Path (Simulated):**
    *   **Test Case:**
        *   Enter a known valid cryptocurrency symbol (e.g., "BTCUSDT") in the "Cryptocurrency Symbol" field.
        *   Select a K-line interval (e.g., "1h").
        *   Enter a placeholder/dummy LLM API Key (e.g., "TEST_KEY_123").
        *   Leave the "LLM API URL" as default or enter a valid one if you have a custom endpoint.
        *   Click the "Analyze Trends 🚀" button.
    *   **Expected Result:**
        *   Loading indicators (`st.spinner`) appear sequentially for "Fetching K-line data..." and then (if data fetching succeeds) "Analyzing trends with LLM...".
        *   **K-line Data Section:**
            *   If your environment can connect to Binance without restriction: This section should display a success message (e.g., "Successfully fetched X K-lines...") and a table/dataframe showing the K-line data (first 20 rows).
            *   If Binance API is restricted (e.g., geo-blocking): This section should display a clear error message (e.g., "Binance API Error: ... This might be due to geo-restrictions...").
        *   **LLM Analysis Section:**
            *   If K-line data fetching failed: This section should either remain empty or display a message indicating that analysis cannot proceed because data is missing (e.g., "Failed to fetch K-line data. Cannot proceed with analysis.").
            *   If K-line data fetching succeeded (even hypothetically): The LLM analysis will be attempted.
                *   With a dummy/invalid API key: This section should display an error related to the LLM API communication (e.g., "LLM Analysis Failed: Error: Failed to get analysis from LLM... This could be due to API key issues...").
                *   (Hypothetically, with a valid API key and successful LLM call): This section would display a success message and the analysis text from the LLM.

4.  **Missing API Key:**
    *   **Test Case:**
        *   Enter a symbol (e.g., "BTCUSDT").
        *   Leave the "Your LLM API Key 🔑" field empty.
        *   Click "Analyze Trends 🚀".
    *   **Expected Result:** An error message "LLM API Key is required. Please enter it in the sidebar. 🔑" should be displayed directly on the page. No spinners for data fetching or analysis should appear.

5.  **Missing Symbol:**
    *   **Test Case:**
        *   Leave the "Cryptocurrency Symbol" field empty.
        *   Enter an API key.
        *   Click "Analyze Trends 🚀".
    *   **Expected Result:** A warning message "Please enter a cryptocurrency symbol." should be displayed. No spinners for data fetching or analysis should appear.

6.  **Interaction & Error Message Clarity:**
    *   **Test Case:** Trigger various error conditions (as in tests 3, 4, and 5). Submit valid inputs after an error to see if the UI updates correctly.
    *   **Expected Result:**
        *   Error messages are displayed clearly, are user-friendly, and appear in the relevant section of the UI (e.g., API key error shown prominently, data fetching errors in the K-line data area).
        *   Placeholders are updated or cleared correctly. For instance, if a previous analysis was shown, and then an API key error occurs on a new attempt, the old analysis should be cleared, and the new error should be displayed.
        *   The UI remains responsive.

*Optional Note for CLI-based Smoke Test (for developers):*
While not a substitute for manual UI testing, you can perform a very basic check for immediate script errors in `streamlit_app.py` by running `streamlit run streamlit_app.py --server.runOnSave false --server.headless true --server.port 8502`. If the command exits quickly without errors, it suggests the script initializes without crashing. This does not test any UI interactions or runtime behavior.

## LLM Configuration

*   **API Key:** You must provide your own API key for a compatible LLM service (e.g., OpenAI). The application prompts for this key when run (CLI) or via a sidebar input (Web UI).
*   **API URL:** The application defaults to using OpenAI's chat completions API endpoint (`https://api.openai.com/v1/chat/completions`), which is defined as `DEFAULT_LLM_API_URL` in `app.py`. You can override this by providing a custom URL when prompted by the CLI or in the Web UI.
*   **Model:** The default model used in the LLM prompt is `gpt-3.5-turbo`. This can be changed directly in the `analyze_with_llm` function in `app.py` if needed.

## Known Limitations

*   **Binance API Restrictions:** The Binance API may have usage restrictions, including rate limits or geo-restrictions (blocking requests from certain geographical locations). The application might not function correctly if run from a restricted IP address.
*   **LLM Analysis Quality:** The quality and accuracy of the trend analysis heavily depend on the capabilities of the chosen LLM, the quality of the prompt, and the data provided. The analysis should not be considered financial advice.
*   **Error Handling:** The application includes basic error handling for API calls and user inputs. However, it can be further expanded for more complex scenarios and edge cases.
*   **Data Volume for LLM:** Very long K-line data series are truncated before being sent to the LLM to keep prompts within reasonable limits. This might affect the analysis if critical data points are omitted.

---
This README provides a comprehensive guide for users and developers of the Cryptocurrency Trend Analyzer.
