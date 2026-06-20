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

# Step 3: Order Class (from previous step)
class Order:
    def __init__(self, order_id, symbol, order_type, price, quantity):
        self.order_id = order_id
        self.symbol = symbol
        self.order_type = order_type # 'BUY' or 'SELL'
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return f"Order {self.order_id}: {self.order_type} {self.quantity} {self.symbol} @ ${self.price:.2f}"

# Step 3: OrderBook Class (from previous step)
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
                # print(f"Added BUY order: {order}") # Commented for cleaner output
        elif order_type == 'SELL':
            with self.sell_lock:
                self.sell_orders.append(order)
                # print(f"Added SELL order: {order}") # Commented for cleaner output
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
        buy_str = "\n  ".join(str(o) for o in self.buy_orders) if self.buy_orders else "  (No buy orders)"
        sell_str = "\n  ".join(str(o) for o in self.sell_orders) if self.sell_orders else "  (No sell orders)"
        return f"Order Book:\nBuy Orders:\n{buy_str}\nSell Orders:\n{sell_str}"

# New in Step 4: MatchingEngine Class (Consumer)
class MatchingEngine(threading.Thread):
    def __init__(self, order_book, stocks, interval=0.1):
        super().__init__()
        self.order_book = order_book
        self.stocks = stocks
        self.interval = interval
        self.running = True

    def run(self):
        while self.running:
            buy_order = self.order_book.get_buy_order()
            sell_order = self.order_book.get_sell_order()

            if buy_order and sell_order:
                # For now, just print that orders are matched. Actual matching logic will come later.
                print(f"\n--- Matched Order ---")
                print(f"  BUY: {buy_order}")
                print(f"  SELL: {sell_order}")
                print(f"---------------------\n")
            elif buy_order:
                # If there's a buy order but no sell order, put it back (simple approach for now)
                # In a real system, it would wait or be partially filled
                with self.order_book.buy_lock:
                    self.order_book.buy_orders.appendleft(buy_order)
            elif sell_order:
                # If there's a sell order but no buy order, put it back
                with self.order_book.sell_lock:
                    self.order_book.sell_orders.appendleft(sell_order)

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
        ticker = PriceTicker(stock, interval=0.5)
        ticker_threads.append(ticker)
        ticker.start()

    # Initialize OrderBook
    order_book = OrderBook()

    # New in Step 4: Start MatchingEngine
    matching_engine = MatchingEngine(order_book, stocks, interval=0.2)
    matching_engine.start()

    # Add some dummy orders to the order book for testing
    print("\n--- Adding Dummy Orders ---")
    order_book.add_order('BUY', 'AAPL', 150.50, 10)
    order_book.add_order('SELL', 'GOOGL', 2805.00, 5)
    order_book.add_order('BUY', 'MSFT', 301.20, 20)
    order_book.add_order('SELL', 'AAPL', 151.00, 7)
    order_book.add_order('BUY', 'GOOGL', 2800.00, 5) # This should match the previous SELL GOOGL
    order_book.add_order('SELL', 'MSFT', 300.00, 20) # This should match the previous BUY MSFT

    try:
        # Let it run for a few seconds to see prices updating and orders matching
        for _ in range(15):
            time.sleep(1) # Har 1 second baad current prices aur order book status print karein
            print("\n--- Current Stock Prices ---")
            for symbol, stock in stocks.items():
                print(stock)
            print("\n--- Current Order Book Status ---")
            print(order_book)

    except KeyboardInterrupt:
        print("\nStopping simulation...")
    finally:
        matching_engine.stop()
        matching_engine.join()
        for ticker in ticker_threads:
            ticker.stop()
        for ticker in ticker_threads:
            ticker.join() # Wait for all threads to finish
        print("All threads stopped.")
    print("\nStep 4 Complete! Order Matching Engine is processing orders.")
