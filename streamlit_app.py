import streamlit as st

# Import necessary functions and constants from app.py
# Ensure app.py is in the same directory or PYTHONPATH is set correctly.
try:
    from app import (
        get_crypto_data,
        get_trend_analysis,
        DEFAULT_LLM_API_URL
    )
    # Import specific exceptions for handling
    from binance.exceptions import BinanceAPIException, BinanceRequestException
    # For type hinting Client constants if used, e.g. Client.KLINE_INTERVAL_1HOUR
    # from binance.client import Client 
except ImportError as e:
    st.error(f"Error importing functions/constants from app.py: {e}. Make sure app.py is in the correct path.")
    # Stop the app if core functions can't be imported
    st.stop() 

# --- Streamlit App UI ---
st.title("Cryptocurrency Trend Analyzer 📈")

st.info(
    "This application fetches historical cryptocurrency K-line data from Binance "
    "and uses a Large Language Model (LLM) to provide trend analysis."
)

# --- Sidebar for Inputs ---
st.sidebar.header("Input Parameters")

symbol = st.sidebar.text_input("Cryptocurrency Symbol", value="BTCUSDT", help="e.g., BTCUSDT, ETHUSDT")
# Common intervals for user convenience. For full list, refer to Binance API docs.
# Example: Client.KLINE_INTERVAL_1HOUR is '1h'
interval_options = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '3d', '1w', '1M']
interval = st.sidebar.selectbox("K-line Interval", options=interval_options, index=5, help="Select the K-line interval (default: 1h)") # Default to '1h'

st.sidebar.markdown("---") # Separator

api_key = st.sidebar.text_input("Your LLM API Key 🔑", type="password", help="Enter your API key for the LLM service.")
llm_api_url = st.sidebar.text_input(
    "LLM API URL (optional)", 
    value=DEFAULT_LLM_API_URL, 
    help=f"Defaults to OpenAI's API. Override if using a different endpoint."
)

st.sidebar.markdown("---") # Separator

# Placeholders for actual data display in the main area
kline_data_placeholder = st.empty()
llm_analysis_placeholder = st.empty()

# --- Analysis Button and Logic ---
if st.sidebar.button("Analyze Trends 🚀"):
    if not api_key:
        st.error("LLM API Key is required. Please enter it in the sidebar. 🔑")
    elif not symbol:
        st.warning("Please enter a cryptocurrency symbol.")
    else:
        # Clear previous results from placeholders
        kline_data_placeholder.empty()
        llm_analysis_placeholder.empty()

        st.subheader("Processing Request...")
        
        # --- 1. Fetch Cryptocurrency Data ---
        crypto_data = None
        with st.spinner(f'Fetching K-line data for {symbol.upper()} ({interval})...'):
            try:
                crypto_data = get_crypto_data(symbol.upper(), interval)
            except BinanceAPIException as e:
                kline_data_placeholder.error(f"Binance API Error: {e}. This might be due to geo-restrictions or an invalid symbol/interval.")
            except BinanceRequestException as e:
                kline_data_placeholder.error(f"Binance Request Error: {e}. Please check the symbol and interval.")
            except Exception as e:
                kline_data_placeholder.error(f"An unexpected error occurred while fetching data: {e}")

        # --- 2. Display K-line Data ---
        if crypto_data:
            kline_data_placeholder.success(f"Successfully fetched {len(crypto_data)} K-lines for {symbol.upper()}.")
            
            # Displaying data - converting to DataFrame for better column names (optional)
            # For now, direct display is fine.
            # Column names for Binance K-line data (subset)
            # [Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, ...]
            st.subheader("Raw K-line Data (first 20 rows):")
            # Create a list of dictionaries for st.dataframe for better display with headers
            display_data = []
            if crypto_data:
                 # Define headers for the most relevant K-line data fields
                headers = [
                    "Open Time", "Open", "High", "Low", "Close", "Volume", 
                    "Close Time", "Quote Asset Volume", "Number of Trades",
                    "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
                ]
                for i, row in enumerate(crypto_data[:20]): # Display first 20 rows
                    # Ensure row has enough elements for headers
                    display_data.append({headers[j]: row[j] for j in range(min(len(row), len(headers)))})
            
            if display_data:
                st.dataframe(display_data)
            else: # crypto_data might be an empty list from the API
                 kline_data_placeholder.warning("Fetched data is empty. Cannot proceed with analysis.")


            # --- 3. Perform Trend Analysis ---
            if crypto_data: # Ensure crypto_data is not None and not empty before proceeding
                with st.spinner('Analyzing trends with LLM... This may take a moment.'):
                    try:
                        analysis_result = get_trend_analysis(
                            crypto_data,
                            symbol.upper(),
                            interval,
                            api_key,
                            llm_api_url
                        )
                        if analysis_result:
                            if "Error:" in analysis_result: # Check if the result string itself is an error message
                                llm_analysis_placeholder.error(f"LLM Analysis Failed: {analysis_result}")
                            else:
                                llm_analysis_placeholder.success("Trend analysis complete!")
                                st.subheader("LLM Trend Analysis:")
                                st.markdown(analysis_result) # Using markdown for better formatting if LLM returns it
                        else:
                            llm_analysis_placeholder.error("Failed to get a valid analysis from the LLM. No response or empty response received.")
                    except Exception as e:
                        llm_analysis_placeholder.error(f"An unexpected error occurred during LLM analysis: {e}")
            else: # This else corresponds to 'if crypto_data:' after fetching
                 if not kline_data_placeholder.empty(): # if no error was already set in kline_data_placeholder
                    kline_data_placeholder.warning("No K-line data fetched or data is empty, skipping LLM analysis.")

        elif not kline_data_placeholder.empty(): # If crypto_data is None, and no error set yet
            # This handles the case where get_crypto_data returns None without raising an exception
            # that was caught above.
            kline_data_placeholder.warning("Failed to fetch K-line data. Cannot proceed with analysis.")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Note:** Ensure your environment is set up with the necessary dependencies (`requirements.txt`). "
    "Binance API may have geo-restrictions."
)

# To run this Streamlit app:
# 1. Make sure 'streamlit' is in your requirements.txt and installed.
# 2. Open your terminal in the project root.
# 3. Run: streamlit run streamlit_app.py
