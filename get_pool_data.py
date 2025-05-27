import pandas as pd
import requests
import time
from typing import Optional
import json
from dotenv import load_dotenv
import os
load_dotenv()
solscan_api_key = os.getenv("SOLSCAN_API_KEY")

class SolanaPoolAnalyzer:
    def __init__(self, pool_address: str, rate_sleep_delay: float = 0.2):
        """
        Initialize the SolanaPoolAnalyzer with pool address and rate delay.
        
        Args:
            pool_address (str): The Solana pool address to analyze
            rate_sleep_delay (float): Delay between API calls in seconds
        """
        self.pool_address = pool_address
        self.rate_sleep_delay = rate_sleep_delay
        self.max_retries = 2

    def _convert_decimals(self, val, decimals):
        """Helper method to convert token amounts using their decimals"""
        return val/10**decimals

    def _make_api_call(self, url, use_mock_data=False):
        """Helper method to make API calls with retry logic"""
        if use_mock_data:
            with open(r"mock_data\mock_data.json", 'r') as file:
                mock_data = json.load(file)
            print(f"Using mock data")
            return mock_data
        else:
            for attempt in range(self.max_retries):
                try:          
                    response = requests.get(url, headers={"token": solscan_api_key})
                    response.raise_for_status() 
                    if not response.text:
                        raise ValueError("Empty response received from API")
                    return response.json()
                except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                    if attempt < self.max_retries - 1:
                        print(f"Request failed: {e}. Retrying...")
                        time.sleep(self.rate_sleep_delay)
                    else:
                        print(f"Failed after {self.max_retries} attempts: {e}")
                        raise
                except ValueError as e:
                    print(f"Error: {e}")
                    raise
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    raise

    def _get_pool_transfer(self, from_date: str, to_date: str, use_mock_data: bool = False):
        """Internal method to get pool transfers"""
        from_time = int(pd.to_datetime(from_date).timestamp())
        to_time = int(pd.to_datetime(to_date).timestamp())
        transactions_all = pd.DataFrame()
        page_number = 1  
        last_block_timestamp = None 
        try:
            while last_block_timestamp is None or last_block_timestamp < to_time:
                url = f"https://pro-api.solscan.io/v2.0/account/transfer?address={self.pool_address}&activity_type[]=ACTIVITY_SPL_TRANSFER&from_time={from_time}&to_time={to_time}&page={page_number}&page_size=100&sort_by=block_time&sort_order=desc"    
                
                if page_number > 1:
                    page_number += 1

                response_in_json = self._make_api_call(url, use_mock_data= use_mock_data)
                transfers = response_in_json.get('data', {})
                
                if last_block_timestamp and not transfers:
                    print(f"Error: {response_in_json.get('errors', {})} - Last page number: {page_number}, Last transaction timestamp: {last_block_timestamp}")
                    break
                if not last_block_timestamp and not transfers:
                    print(f"Error: {response_in_json.get('errors', {})}")
                    break

                transactions = pd.DataFrame(transfers)
                ### caching moment, save the transactions to a temp table or just retaing the data on logs
                if not transactions.empty:
                    last_block_timestamp = transactions.iloc[0]["block_time"]
                    page_number = response_in_json.get('page_number', {}) 
                    transactions_all = pd.concat([transactions_all, transactions])
                
                if not page_number:
                        break
                time.sleep(self.rate_sleep_delay) 
        except Exception as e:
            if not transactions_all.empty:
                print(f"Error ocurred while fetching transactions: {e}, last transaction timestamp: {last_block_timestamp}")
                return transactions_all
            else:
                print(f"Error: {e}")
                raise
            
        return transactions_all

    def _pool_transfers_data_processing(self, transactions_all: pd.DataFrame):
        """Internal method to process pool transfers data"""
        transactions_all['datetime'] = pd.to_datetime(transactions_all['time']).dt.strftime('%Y-%m-%d %H:%M:%S')
        transactions_all['datetime'] = pd.to_datetime(transactions_all['datetime'])
        transactions_all["timestamp"] = transactions_all['block_time'].astype(int)
        transactions_all["amount"] = self._convert_decimals(transactions_all["amount"], transactions_all["token_decimals"])
        
        columns_to_keep = ["trans_id", "datetime", "timestamp", "amount", "from_address", "to_address", "token_address", "flow"]
        return transactions_all[columns_to_keep]

    def _final_table_data_process(self, processed: pd.DataFrame):
        """Internal method to create final processed table"""
        processed_in = processed[processed.flow == "in"]
        processed_out = processed[processed.flow == "out"]
        processed = processed_in.merge(processed_out[["trans_id",'amount', 'token_address', 'flow']], on="trans_id")
        processed.rename(columns={
            "amount_x": "amount_in", 
            "amount_y": "amount_out",
            "from_address": "owner_address",
            "token_address_x": "token_in_address",
            "token_address_y": "token_out_address"
        }, inplace=True)
        
        return processed[["trans_id", "datetime", "timestamp", "owner_address", "token_in_address", "amount_in", "token_out_address", "amount_out"]]

    def get_swaps(self, from_date: str, to_date: str, use_mock_data: bool = False) -> pd.DataFrame:
        """
        Get processed swap data for the pool within the specified date range.
        
        Args:
            from_date (str): Start date in format 'YYYY-MM-DD'
            to_date (str): End date in format 'YYYY-MM-DD'
            
        Returns:
            pd.DataFrame: Processed swap data with the following columns:
                - trans_id: Transaction ID
                - datetime: Transaction datetime
                - timestamp: Transaction timestamp
                - owner_address: Address of the swap initiator
                - token_in_address: Address of the input token
                - amount_in: Amount of input token
                - token_out_address: Address of the output token
                - amount_out: Amount of output token
        """
        # Get raw transfers
        raw_transfers = self._get_pool_transfer(from_date, to_date, use_mock_data=use_mock_data)
        
        # Process the transfers
        processed_transfers = self._pool_transfers_data_processing(raw_transfers)
        
        # Create final table
        final_table = self._final_table_data_process(processed_transfers)
        
        return final_table 
    


### test #### 
    
if __name__ == "__main__":
    pool_analyzer = SolanaPoolAnalyzer(pool_address="8phK65jxmTPEN158xLgSr4oZvssw9SyTErpNZj3g7px4")
    swaps = pool_analyzer.get_swaps(from_date="2024-07-01", to_date="2024-07-02", use_mock_data=True)
    print(swaps)    
