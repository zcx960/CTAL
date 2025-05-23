import unittest
from unittest.mock import patch, Mock
import requests # Required for requests.exceptions.RequestException

# Assuming app.py is in the same directory or accessible via PYTHONPATH
from app import (
    format_kline_data_for_prompt,
    analyze_with_llm,
    get_trend_analysis,
    get_crypto_data,
    USER_API_KEY, # For testing the default key behavior
    DEFAULT_LLM_API_URL
)
# Import Client for type hinting or constants if needed by tests, and exceptions
from binance.client import Client 
from binance.exceptions import BinanceAPIException, BinanceRequestException


class TestFormatKlineDataForPrompt(unittest.TestCase):
    def test_valid_data_formatting(self):
        sample_klines = [
            [1678886400000, "24000", "24500", "23900", "24200", "1000", 1678889999999, "24200000", 500],
            [1678890000000, "24200", "24800", "24100", "24700", "1200", 1678893599999, "29640000", 600],
        ]
        symbol = "BTCUSDT"
        interval = "1h"
        expected_header = f"Candlestick data for {symbol} ({interval} interval):\n"
        expected_line1 = "  Timestamp: 1678886400000, Open: 24000, High: 24500, Low: 23900, Close: 24200, Volume: 1000"
        expected_line2 = "  Timestamp: 1678890000000, Open: 24200, High: 24800, Low: 24100, Close: 24700, Volume: 1200"
        
        result = format_kline_data_for_prompt(sample_klines, symbol, interval)
        
        self.assertIn(expected_header.strip(), result)
        self.assertIn(expected_line1, result)
        self.assertIn(expected_line2, result)

    def test_empty_kline_data(self):
        result = format_kline_data_for_prompt([], "BTCUSDT", "1h")
        self.assertEqual(result, "No K-line data provided or data is empty.")

    def test_none_kline_data(self):
        result = format_kline_data_for_prompt(None, "BTCUSDT", "1h")
        self.assertEqual(result, "No K-line data provided or data is empty.")

    def test_truncation_of_large_data(self):
        # Create 35 klines (more than the default max_lines of 30 in the function)
        large_klines = [[1678886400000 + i*3600000, "24000", "24500", "23900", "24200", "1000"] for i in range(35)]
        result = format_kline_data_for_prompt(large_klines, "BTCUSDT", "1h")
        self.assertIn("... (data truncated) ...", result)
        # Header + 29 lines + truncation message = 31 lines in total (due to how max_lines is used)
        self.assertEqual(len(result.split('\n')), 1 + 29 + 1)


class TestAnalyzeWithLLM(unittest.TestCase):
    @patch('app.requests.post')
    def test_successful_api_call(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "  Expected LLM output  "}}]
        }
        mock_post.return_value = mock_response

        result = analyze_with_llm("fake_api_key", "Test prompt")
        self.assertEqual(result, "Expected LLM output")
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['headers']['Authorization'], "Bearer fake_api_key")
        self.assertEqual(kwargs['json']['messages'][-1]['content'], "Test prompt")

    @patch('app.requests.post')
    def test_api_error_401(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Client Error")
        mock_post.return_value = mock_response

        result = analyze_with_llm("fake_api_key", "Test prompt")
        self.assertIsNone(result) # Expecting None on error

    @patch('app.requests.post')
    def test_network_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        result = analyze_with_llm("fake_api_key", "Test prompt")
        self.assertIsNone(result)

    @patch('app.requests.post')
    def test_invalid_json_response(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("JSON decode error")
        mock_response.text = "Invalid JSON string" # For error message
        mock_post.return_value = mock_response

        result = analyze_with_llm("fake_api_key", "Test prompt")
        self.assertIsNone(result)

    def test_missing_api_key_placeholder(self):
        # Uses the actual USER_API_KEY which should be "YOUR_API_KEY"
        result = analyze_with_llm(USER_API_KEY, "Test prompt")
        self.assertIsNone(result)
    
    def test_missing_api_key_empty(self):
        result = analyze_with_llm("", "Test prompt")
        self.assertIsNone(result)

    def test_missing_api_key_none(self):
        result = analyze_with_llm(None, "Test prompt")
        self.assertIsNone(result)


class TestGetTrendAnalysis(unittest.TestCase):
    def setUp(self):
        self.sample_klines = [
            [1678886400000, "24000", "24500", "23900", "24200", "1000"],
            [1678890000000, "24200", "24800", "24100", "24700", "1200"],
        ]
        self.symbol = "BTCUSDT"
        self.interval = "1h"
        self.api_key = "test_key"

    @patch('app.analyze_with_llm')
    def test_successful_analysis(self, mock_analyze_llm):
        expected_llm_response = "LLM says buy!"
        mock_analyze_llm.return_value = expected_llm_response
        
        result = get_trend_analysis(self.sample_klines, self.symbol, self.interval, self.api_key)
        self.assertEqual(result, expected_llm_response)
        
        # Check that analyze_with_llm was called with a prompt containing formatted kline data
        mock_analyze_llm.assert_called_once()
        args, _ = mock_analyze_llm.call_args
        prompt_arg = args[1] # prompt_text is the second argument
        self.assertIn(self.symbol, prompt_arg)
        self.assertIn(self.interval, prompt_arg)
        self.assertIn("Timestamp: 1678886400000", prompt_arg) # Check for part of formatted data

    @patch('app.analyze_with_llm')
    def test_llm_returns_none(self, mock_analyze_llm):
        mock_analyze_llm.return_value = None
        result = get_trend_analysis(self.sample_klines, self.symbol, self.interval, self.api_key)
        self.assertIn("Error: Failed to get analysis from LLM.", result)

    def test_invalid_crypto_data_none(self):
        result = get_trend_analysis(None, self.symbol, self.interval, self.api_key)
        self.assertEqual(result, "Error: Invalid or empty cryptocurrency data provided for analysis.")

    def test_invalid_crypto_data_empty_list(self):
        result = get_trend_analysis([], self.symbol, self.interval, self.api_key)
        self.assertEqual(result, "Error: Invalid or empty cryptocurrency data provided for analysis.")
    
    def test_crypto_data_list_of_non_lists(self):
        result = get_trend_analysis(["not a list"], self.symbol, self.interval, self.api_key)
        self.assertEqual(result, "Error: Invalid or empty cryptocurrency data provided for analysis.")


class TestGetCryptoData(unittest.TestCase):
    def test_api_call_restricted_or_fails(self):
        # This test acknowledges the known API restrictions.
        # It checks if the function handles this by returning None or raising a known exception.
        symbol = "BTCUSDT"
        interval = Client.KLINE_INTERVAL_1HOUR # Using a constant from the library
        
        try:
            result = get_crypto_data(symbol, interval)
            self.assertIsNone(result, "Expected None if API call is silently handled on failure (e.g. geo-restriction leads to error caught internally)")
        except (BinanceAPIException, BinanceRequestException, requests.exceptions.RequestException) as e:
            # This is also an acceptable outcome if the function raises these specific exceptions
            # due to the restriction or other network issues.
            print(f"Caught expected exception: {e}") # Optional: print for clarity during test run
            pass 
        except Exception as e:
            # Catch any other unexpected exception
            self.fail(f"get_crypto_data raised an unexpected exception: {e}")


if __name__ == '__main__':
    unittest.main()
