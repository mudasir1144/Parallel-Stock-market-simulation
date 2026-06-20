# main.py
import time
import random
import threading

# Step 1: Basic Stock Model
class Stock:
    def __init__(self, symbol, initial_price):
        self.symbol = symbol
        self.price = initial_price

    def __str__(self):
        return f"{self.symbol}: ${self.price:.2f}"

# Initialize some stocks (Market mein 5 stocks add kiye hain)
stocks = {
    "AAPL": Stock("AAPL", 150.0),
    "GOOGL": Stock("GOOGL", 2800.0),
    "MSFT": Stock("MSFT", 300.0),
    "TSLA": Stock("TSLA", 700.0),
    "AMZN": Stock("AMZN", 3300.0)
}

if __name__ == "__main__":
    print("--- Initial Stock Prices ---")
    for symbol, stock in stocks.items():
        print(stock)
    print("\nStep 1 Complete! Basic structure is ready.")
