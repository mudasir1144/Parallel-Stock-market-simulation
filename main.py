# main.py
import time
import random
import threading

# Step 1: Basic Stock Model (from previous step)
class Stock:
    def __init__(self, symbol, initial_price):
        self.symbol = symbol
        self.price = initial_price
        self.lock = threading.Lock() # Har stock ka apna lock hoga

    def update_price(self, change):
        with self.lock:
            self.price += change
            if self.price < 0.01: # Price negative na ho jaye
                self.price = 0.01

    def get_price(self):
        with self.lock:
            return self.price

    def __str__(self):
        return f"{self.symbol}: ${self.get_price():.2f}"

# Step 2: Price Ticker Thread (Producer)
class PriceTicker(threading.Thread):
    def __init__(self, stock, interval=1):
        super().__init__()
        self.stock = stock
        self.interval = interval
        self.running = True

    def run(self):
        while self.running:
            # Random price change (-1.0 to +1.0)
            change = random.uniform(-1.0, 1.0)
            self.stock.update_price(change)
            # print(f"Updated {self.stock.symbol} to {self.stock.get_price():.2f}") # For debugging
            time.sleep(self.interval)

    def stop(self):
        self.running = False

# Initialize some stocks
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

    print("\n--- Starting Price Tickers ---")
    ticker_threads = []
    for symbol, stock in stocks.items():
        ticker = PriceTicker(stock, interval=0.5) # Har 0.5 second mein price update hogi
        ticker_threads.append(ticker)
        ticker.start()

    try:
        # Let it run for a few seconds to see prices updating
        for _ in range(10):
            time.sleep(1) # Har 1 second baad current prices print karein
            print("\n--- Current Stock Prices ---")
            for symbol, stock in stocks.items():
                print(stock)

    except KeyboardInterrupt:
        print("\nStopping tickers...")
    finally:
        for ticker in ticker_threads:
            ticker.stop()
        for ticker in ticker_threads:
            ticker.join() # Wait for all threads to finish
        print("All tickers stopped.")
    print("\nStep 2 Complete! Live price feed is working.")
