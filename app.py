from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
import requests # Moved import to top level

# Main application logic will go here

def get_crypto_data(symbol: str, interval: str):
    """
    Fetches historical K-line (candlestick) data for the given symbol and interval from Binance.

    Args:
        symbol: The trading symbol (e.g., 'BTCUSDT').
        interval: The interval for K-lines (e.g., Client.KLINE_INTERVAL_1HOUR, '1d', '1w').
                  Refer to python-binance documentation for valid intervals.

    Returns:
        A list of K-line data if successful, None otherwise.
        Each K-line is a list:
        [
            Open time,
            Open,
            High,
            Low,
            Close,
            Volume,
            Close time,
            Quote asset volume,
            Number of trades,
            Taker buy base asset volume,
            Taker buy quote asset volume,
            Ignore
        ]
    """
    client = Client()  # No API key needed for public data

    try:
        # Fetch klines for the last 1 day. The start_str can be adjusted.
        # For example, "1 day ago UTC", "1 Dec, 2017", "1 Jan, 2017"
        # The interval can also be set using Client constants, e.g., Client.KLINE_INTERVAL_1HOUR
        klines = client.get_historical_klines(symbol, interval, "1 day ago UTC")
        return klines
    except BinanceAPIException as e:
        print(f"Binance API Exception: {e}")
        return None
    except BinanceRequestException as e:
        print(f"Binance Request Exception: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# Placeholder for the user's OpenAI API key
# IMPORTANT: Replace "YOUR_API_KEY" with your actual OpenAI API key.
# It is recommended to use environment variables or a secure key management system for production.
USER_API_KEY = "YOUR_API_KEY"

# Default OpenAI API URL. Users can override this if they use a different endpoint or a proxy.
DEFAULT_LLM_API_URL = "https://api.openai.com/v1/chat/completions"

def analyze_with_llm(api_key: str, prompt_text: str, llm_api_url: str = None):
    """
    Sends a prompt to an LLM API (defaulting to OpenAI's chat completions endpoint)
    and returns the text content of the response.

    Args:
        api_key: The API key for the LLM service.
        prompt_text: The user's prompt to send to the LLM.
        llm_api_url: Optional. The API URL for the LLM service.
                     Defaults to DEFAULT_LLM_API_URL if None.

    Returns:
        The text content from the LLM's response if successful, None otherwise.
    """
    if api_key == "YOUR_API_KEY" or not api_key:
        print("Error: API key not configured. Please set USER_API_KEY in app.py.")
        return None

    api_url = llm_api_url if llm_api_url else DEFAULT_LLM_API_URL

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Standard OpenAI API request structure
    # You might need to adjust the model or other parameters based on the specific LLM provider.
    data = {
        "model": "gpt-3.5-turbo",  # Or any other model like gpt-4
        "messages": [
            {"role": "system", "content": "You are a helpful assistant providing financial market analysis."},
            {"role": "user", "content": prompt_text}
        ]
        # Add other parameters like temperature, max_tokens if needed
    }

    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

        response_json = response.json()

        # Extract text content - this might vary based on the LLM API's response structure
        # For OpenAI, it's typically in response_json['choices'][0]['message']['content']
        if response_json.get("choices") and \
           len(response_json["choices"]) > 0 and \
           response_json["choices"][0].get("message") and \
           response_json["choices"][0]["message"].get("content"):
            return response_json["choices"][0]["message"]["content"].strip()
        else:
            print(f"Error: Unexpected response format from LLM API: {response_json}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Network error or API error communicating with LLM: {e}")
        return None
    except ValueError: # Handles JSON decoding errors
        print(f"Error: Could not decode JSON response from LLM API: {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during LLM analysis: {e}")
        return None

def format_kline_data_for_prompt(kline_data, symbol: str, interval: str) -> str:
    """
    Formats K-line data into a human-readable string for LLM prompts.

    Args:
        kline_data: List of K-line data. Each kline is a list.
        symbol: The trading symbol (e.g., 'BTCUSDT').
        interval: The interval of the K-lines (e.g., '1h', '1d').

    Returns:
        A string representation of the K-line data, or an error message if data is invalid.
    """
    if not kline_data:
        return "No K-line data provided or data is empty."

    header = f"Candlestick data for {symbol} ({interval} interval):\n"
    data_str_lines = [header]

    # K-line format from Binance:
    # [Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades,
    #  Taker buy base asset volume, Taker buy quote asset volume, Ignore]
    for kline in kline_data:
        try:
            # Convert timestamp to a more readable format if needed, for now, using raw open time
            # For LLMs, providing raw, structured data is often effective.
            # Consider converting Open time (kline[0]) and Close time (kline[6]) to datetime strings
            # if the LLM struggles with raw timestamps. e.g., using datetime.fromtimestamp(kline[0]/1000)
            line = (
                f"  Timestamp: {kline[0]}, Open: {kline[1]}, High: {kline[2]}, Low: {kline[3]}, "
                f"Close: {kline[4]}, Volume: {kline[5]}"
            )
            data_str_lines.append(line)
        except (IndexError, TypeError) as e:
            data_str_lines.append(f"  Error formatting kline: {kline} - {e}")
            continue # Skip malformed klines

    # Limit the amount of data sent to the LLM to avoid overly long prompts
    # This is a simple truncation, more sophisticated sampling/summarization could be used.
    max_lines = 30  # Example limit, adjust as needed
    if len(data_str_lines) > max_lines:
        data_str_lines = data_str_lines[:max_lines-1] + ["  ... (data truncated) ..."]

    return "\n".join(data_str_lines)

def get_trend_analysis(crypto_data, symbol: str, interval: str, api_key: str, llm_api_url: str = None):
    """
    Generates a trend analysis prompt from cryptocurrency data and sends it to an LLM.

    Args:
        crypto_data: The structured cryptocurrency data (list of K-lines).
        symbol: The trading symbol (e.g., 'BTCUSDT').
        interval: The interval of the K-lines (e.g., '1h', '1d').
        api_key: The user's LLM API key.
        llm_api_url (optional): The URL for the LLM API.

    Returns:
        The analysis text received from the LLM, or an error message.
    """
    if not crypto_data or not isinstance(crypto_data, list) or not all(isinstance(item, list) for item in crypto_data):
        return "Error: Invalid or empty cryptocurrency data provided for analysis."

    formatted_data_str = format_kline_data_for_prompt(crypto_data, symbol, interval)
    if "No K-line data provided" in formatted_data_str or "Error formatting kline" in formatted_data_str:
        # If formatting itself had issues (e.g. completely empty initial data)
        return f"Error: Could not format K-line data for LLM prompt. Details: {formatted_data_str}"

    prompt = (
        f"Analyze the following candlestick data for {symbol} with {interval} candles. "
        "Identify potential trends (e.g., uptrend, downtrend, consolidation), "
        "key support and resistance levels, and provide potential trading suggestions "
        "(e.g., buy, sell, hold) with concise reasoning based *only* on the provided data. "
        "Avoid general advice. Focus on patterns and indicators visible in the data.\n\n"
        f"Data:\n{formatted_data_str}"
    )

    print("\n--- Generated LLM Prompt ---")
    print(prompt)
    print("--- End of LLM Prompt ---\n")

    analysis_result = analyze_with_llm(api_key, prompt, llm_api_url)

    if analysis_result:
        return analysis_result
    else:
        return "Error: Failed to get analysis from LLM. The LLM call did not return a result. This could be due to API key issues, network problems, or an issue with the LLM service."


import getpass

if __name__ == '__main__':
    print("Welcome to the Crypto Trend Analyzer!")
    print("This tool fetches cryptocurrency data and uses an LLM to provide a trend analysis.")
    print("-" * 50)

    # --- User Inputs ---
    user_crypto_symbol = input("Enter the cryptocurrency symbol (e.g., BTCUSDT, ETHUSDT): ").upper()

    print("\nEnter the K-line interval.")
    print("Common intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M")
    print(f"You can also use constants like Client.{Client.KLINE_INTERVAL_1HOUR}, Client.{Client.KLINE_INTERVAL_1DAY}, etc.")
    user_kline_interval = input("Interval: ")

    print("\nEnter your LLM API Key.")
    print("This will be used to make requests to the LLM for analysis.")
    try:
        user_llm_api_key = getpass.getpass("LLM API Key: ")
    except ImportError: # Fallback for environments where getpass might not be available
        print("(getpass not available, using simple input. API key will be visible.)")
        user_llm_api_key = input("LLM API Key: ")
    except Exception: # Catch other getpass related errors, e.g., Inappropriate ioctl for device
        print("(getpass failed, using simple input. API key will be visible.)")
        user_llm_api_key = input("LLM API Key: ")


    user_llm_api_url = input(f"Enter custom LLM API URL (or press Enter to use default: {DEFAULT_LLM_API_URL}): ")
    if not user_llm_api_url:
        user_llm_api_url = DEFAULT_LLM_API_URL
        print(f"Using default LLM API URL: {user_llm_api_url}")

    print("-" * 50)
    print("Fetching cryptocurrency data...")

    # --- Application Flow ---
    # Note: The USER_API_KEY global variable is now less relevant for the API key itself,
    # as we are prompting the user. It still serves as an example in the file.
    # The DEFAULT_LLM_API_URL is used as intended.

    crypto_data = None
    try:
        crypto_data = get_crypto_data(user_crypto_symbol, user_kline_interval)
    except BinanceAPIException as e:
        print(f"Error fetching crypto data from Binance: {e}")
        print("This might be due to API restrictions (e.g., geo-blocking) or an invalid symbol/interval.")
        print("You can try with a different symbol/interval or check your network connection.")
    except Exception as e:
        print(f"An unexpected error occurred during data fetching: {e}")

    if crypto_data:
        print(f"Successfully fetched {len(crypto_data)} k-line data points for {user_crypto_symbol}.")
        print("-" * 50)
        print("Requesting trend analysis from LLM...")

        # Pass the user-provided API key and URL
        analysis_result = get_trend_analysis(
            crypto_data,
            user_crypto_symbol,
            user_kline_interval,
            user_llm_api_key, # Use the key provided by the user
            user_llm_api_url  # Use the URL provided by the user or default
        )

        print("-" * 50)
        if analysis_result:
            if "Error:" in analysis_result: # Check if the result itself is an error message from our functions
                print(f"Trend Analysis Error: {analysis_result}")
            else:
                print("Trend Analysis Result:")
                print(analysis_result)
        else:
            # This case should ideally be covered by error messages within get_trend_analysis
            print("Failed to get trend analysis. No specific error message was returned.")

    elif crypto_data is None and 'e' not in locals(): # Only print if no BinanceAPIException was caught
        print("No data fetched. Cannot proceed with trend analysis.")
    elif crypto_data == []: # Explicitly check for empty list if API returns that for some valid queries
        print("Fetched data is empty. Cannot proceed with trend analysis.")


    print("-" * 50)
    print("CLI session finished.")


