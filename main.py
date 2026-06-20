# main.py
import time
import random
import threading
from collections import deque

# Step 1: Basic Stock Model (from previous step)
class Stock:
    def __init__(self, symbol, initial_price):
        self.symbol = symbol
        self.price = initial_price
        self.lock = threading.Lock() # Har stock ka apna lock hoga

    def update_price(self, change):
        with self.lock:
            self.price += change
            if self.price < 0.01:
                self.price = 0.01

    def get_price(self):
        with self.lock:
            return self.price

    def __str__(self):
        return f"{self.symbol}: ${self.get_price():.2f}"

# Step 2: Price Ticker Thread (Producer) (from previous step)
class PriceTicker(threading.Thread):
    def __init__(self, stock, interval=1):
        super().__init__()
        self.stock = stock
        self.interval = interval
        self.running = True

    def run(self):
        while self.running:
            change = random.uniform(-1.0, 1.0)
            self.stock.update_price(change)
            time.sleep(self.interval)

    def stop(self):
        self.running = False

# New in Step 3: Order Class
class Order:
    def __init__(self, order_id, symbol, order_type, price, quantity):
        self.order_id = order_id
        self.symbol = symbol
        self.order_type = order_type # 'BUY' or 'SELL'
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return f"Order {self.order_id}: {self.order_type} {self.quantity} {self.symbol} @ ${self.price:.2f}"

# New in Step 3: OrderBook Class
class OrderBook:
    def __init__(self):
        self.buy_orders = deque()  # Queue for buy orders
        self.sell_orders = deque() # Queue for sell orders
        self.buy_lock = threading.Lock()
        self.sell_lock = threading.Lock()
        self.order_id_counter = 0
        self.counter_lock = threading.Lock()

    def generate_order_id(self):
        with self.counter_lock:
            self.order_id_counter += 1
            return self.order_id_counter

    def add_order(self, order_type, symbol, price, quantity):
        order_id = self.generate_order_id()
        order = Order(order_id, symbol, order_type, price, quantity)
        if order_type == 'BUY':
            with self.buy_lock:
                self.buy_orders.append(order)
                print(f"Added BUY order: {order}")
        elif order_type == 'SELL':
            with self.sell_lock:
                self.sell_orders.append(order)
                print(f"Added SELL order: {order}")
        return order

    def get_buy_order(self):
        with self.buy_lock:
            if self.buy_orders:
                return self.buy_orders.popleft()
        return None

    def get_sell_order(self):
        with self.sell_lock:
            if self.sell_orders:
                return self.sell_orders.popleft()
        return None

    def __str__(self):
        buy_str = "\n  ".join(str(o) for o in self.buy_orders)
        sell_str = "\n  ".join(str(o) for o in self.sell_orders)
        return f"Order Book:\nBuy Orders:\n  {buy_str}\nSell Orders:\n  {sell_str}"

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
        ticker = PriceTicker(stock, interval=0.5)
        ticker_threads.append(ticker)
        ticker.start()

    # New in Step 3: Initialize OrderBook
    order_book = OrderBook()

    # Add some dummy orders to the order book
    print("\n--- Adding Dummy Orders ---")
    order_book.add_order('BUY', 'AAPL', 150.50, 10)
    order_book.add_order('SELL', 'GOOGL', 2805.00, 5)
    order_book.add_order('BUY', 'MSFT', 301.20, 20)
    order_book.add_order('SELL', 'AAPL', 151.00, 7)

    try:
        for _ in range(5):
            time.sleep(1)
            print("\n--- Current Stock Prices ---")
            for symbol, stock in stocks.items():
                print(stock)
            print("\n--- Current Order Book Status ---")
            print(order_book)

    except KeyboardInterrupt:
        print("\nStopping tickers...")
    finally:
        for ticker in ticker_threads:
            ticker.stop()
        for ticker in ticker_threads:
            ticker.join()
        print("All tickers stopped.")
    print("\nStep 3 Complete! Order Book with locks is ready.")
