# Solana Pool Analyser 
### Get swaps by user on a specif timeframe
This project provides a tool to analyze and track swap transactions in Solana pools. It uses the Solscan API to fetch and process pool transfer data, making it easy to analyze trading activity within specific time periods.

## 🚀 Features

- Fetch and analyze pool transfers from Solana blockchain
- Process swap transactions with detailed information
- Support for mock data testing
- Rate limiting and retry mechanisms for API calls
- Data processing and formatting capabilities

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.7 or higher
- pip (Python package installer)

## 🔧 Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
- On Windows:
```bash
.\venv\Scripts\activate
```
- On macOS/Linux:
```bash
source venv/bin/activate
```

4. Install the required dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the project root and add your Solscan API key:
```
SOLSCAN_API_KEY=your_api_key_here
```

## 🎮 Usage

Here's a basic example of how to use the SolanaPoolAnalyzer:

```python
from get_pool_data import SolanaPoolAnalyzer

# Initialize the analyzer with a pool address
pool_analyzer = SolanaPoolAnalyzer(pool_address="your_pool_address")

# Get swap data for a specific date range
swaps = pool_analyzer.get_swaps(
    from_date="2024-01-01",
    to_date="2024-01-02",
    use_mock_data=False  # Set to True to use mock data
)

# Print the results
print(swaps)
```

### 📊 Output Format

The output DataFrame contains the following columns:
- `trans_id`: Transaction ID
- `datetime`: Transaction datetime
- `timestamp`: Transaction timestamp
- `owner_address`: Address of the swap initiator
- `token_in_address`: Address of the input token
- `amount_in`: Amount of input token
- `token_out_address`: Address of the output token
- `amount_out`: Amount of output token

## 🔍 Testing with Mock Data

The project includes mock data for testing purposes. To use mock data, set `use_mock_data=True` when calling `get_swaps()`.

## ⚠️ Rate Limiting

The script includes built-in rate limiting to prevent API throttling. By default, there's a 0.2-second delay between API calls. You can adjust this by modifying the `rate_sleep_delay` parameter when initializing the SolanaPoolAnalyzer.

## Next Steps and enhacements
[] double test function using real calls and data
[] analyse integration of ThreadPoolExecutor to optmize execution time 
[] integrate caching and logging for data extraction


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details. 