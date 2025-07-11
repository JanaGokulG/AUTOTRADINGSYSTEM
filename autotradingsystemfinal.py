import yfinance as yf
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pytz
import pandas as pd
# Dictionary to keep track of owned stocks and their purchase prices
portfolio = {}
# List to keep track of all transactions (buy/sell history)
transactions = []
# Strategies for buy/sell suggestion
def strategy_1(current_price, last_prices):
    # Buy at a low price and sell at a high price (using min/max of last prices)
    if len(last_prices) > 3:
        min_price = min(last_prices)
        max_price = max(last_prices)
        if current_price <= min_price:  # Buy when the price is the lowest in recent data
            return "Buy Now"
        elif current_price >= max_price:  # Sell when the price is the highest in recent data
            return "Sell Now"
    return "Hold"
def strategy_2(current_price, last_prices):
    # Buy at a low price and sell at a high price (using min/max of last prices)
    if len(last_prices) < 5:
        return "Hold"
    min_price = min(last_prices[-5:])
    max_price = max(last_prices[-5:])
    if current_price <= min_price:  # Buy when the price is the lowest
        return "Buy Now"
    elif current_price >= max_price:  # Sell when the price is the highest
        return "Sell Now"
    return "Hold"
def strategy_3(current_price, last_prices):
    # Buy at a low price and sell at a high price (using min/max of last prices)
    if len(last_prices) < 10:
        return "Hold"
    min_price = min(last_prices[-10:])
    max_price = max(last_prices[-10:])
    if current_price <= min_price:  # Buy when the price is the lowest
        return "Buy Now"
    elif current_price >= max_price:  # Sell when the price is the highest
        return "Sell Now"
    return "Hold"
# Placeholder for strategies
def get_suggestion(symbol, current_price, last_prices):
    suggestions = []

    suggestions.append(strategy_1(current_price, last_prices))
    suggestions.append(strategy_2(current_price, last_prices))
    suggestions.append(strategy_3(current_price, last_prices))

    # Most common suggestion
    return max(set(suggestions), key=suggestions.count)
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    history = stock.history(period='1d', interval='5m')

    if history.empty:
        return None

    # Convert to the local time zone
    local_timezone = pytz.timezone("Asia/Kolkata")  # Change as per your local timezone
    history.index = history.index.tz_convert(local_timezone)

    # Convert time to 12-hour AM/PM format
    history['Time'] = history.index.strftime("%I:%M %p")

    return history
def update_display():
    symbol = stock_entry.get().upper()
    history = get_stock_data(symbol)

    if history is None:
        messagebox.showerror("Error", "No data available for the given stock symbol.")
        return

    # Clear existing data in Stock Data table
    for row in transaction_history_tree.get_children():
        transaction_history_tree.delete(row)

    for row in portfolio_tree.get_children():
        portfolio_tree.delete(row)

    last_prices = []
    for index, row in history.iterrows():
        suggestion = get_suggestion(symbol, row['Close'], last_prices)
        # Insert stock data in the Stock Data table (not the Transaction History table)
        stock_data_tree.insert("", "end", values=(row['Time'], f"${row['Close']:.2f}", suggestion))
        last_prices.append(row['Close'])

    # Update Graph
    ax.clear()
    ax.plot(history['Time'], history['Close'], marker='o', linestyle='-', color='b', label="Close Price")
    ax.set_title(f"Stock Price of {symbol}")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price ($)")
    ax.tick_params(axis='x', rotation=45)
    ax.legend(loc="upper left")
    ax.set_xticks(range(0, len(history), max(1, len(history) // 10)))
    ax.set_xticklabels(history['Time'][::max(1, len(history) // 10)], rotation=45)

    canvas.draw()
def buy_stock():
    symbol = stock_entry.get().upper()
    history = get_stock_data(symbol)

    if history is None:
        messagebox.showerror("Error", "No data available for the given stock symbol.")
        return

    last_entry = history.iloc[-1]
    price = last_entry['Close']

    # Add to portfolio
    if symbol in portfolio:
        portfolio[symbol]['quantity'] += 1
    else:
        portfolio[symbol] = {'quantity': 1, 'price': price}

    # Log transaction (buy)
    transactions.append({
        'action': 'Buy',
        'symbol': symbol,
        'price': price,
        'quantity': 1,
        'time': last_entry['Time']
    })

    messagebox.showinfo("Buy Stock", f"Buying {symbol}\nPrice: ${price:.2f} (at {last_entry['Time']})")
    update_portfolio()
    update_transaction_history()

def sell_stock():
    symbol = stock_entry.get().upper()

    if symbol not in portfolio or portfolio[symbol]['quantity'] == 0:
        messagebox.showerror("Error", "You don't own any of this stock.")
        return

    history = get_stock_data(symbol)

    if history is None:
        messagebox.showerror("Error", "No data available for the given stock symbol.")
        return

    last_entry = history.iloc[-1]
    price = last_entry['Close']

    # Sell one share of the stock
    portfolio[symbol]['quantity'] -= 1

    if portfolio[symbol]['quantity'] == 0:
        del portfolio[symbol]

    # Log transaction (sell)
    transactions.append({
        'action': 'Sell',
        'symbol': symbol,
        'price': price,
        'quantity': 1,
        'time': last_entry['Time']
    })

    messagebox.showinfo("Sell Stock", f"Selling {symbol}\nPrice: ${price:.2f} (at {last_entry['Time']})")
    update_portfolio()
    update_transaction_history()

def update_portfolio():
    for row in portfolio_tree.get_children():
        portfolio_tree.delete(row)

    for symbol, data in portfolio.items():
        portfolio_tree.insert("", "end", values=(symbol, data['quantity'], f"${data['price']:.2f}"))

def update_transaction_history():
    # This is used to update the transaction history table for buy/sell actions
    for row in transaction_history_tree.get_children():
        transaction_history_tree.delete(row)

    for transaction in transactions:
        transaction_history_tree.insert("", "end", values=(transaction['time'], transaction['action'], transaction['symbol'], transaction['quantity'], f"${transaction['price']:.2f}"))

def show_disclaimer():
    messagebox.showinfo("Disclaimer", "This stock trading system is for educational purposes only. All trades are simulated.")

def on_exit():
    if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
        messagebox.showinfo("Thank You", "Thank you for using the stock trading system!\n -developed by JANA GOKUL and SAJIN")
        root.quit()

# GUI Setup
root = tk.Tk()
root.title("Stock Trading System")

# Show disclaimer
show_disclaimer()

# Create Notebook for Tabs
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, padx=10, pady=10)

# Create Frames for Tabs
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
notebook.add(tab1, text="Stock Data")
notebook.add(tab2, text="Transaction History")

# Frame for Graph and Tables (Tab 1)
frame = tk.Frame(tab1)
frame.grid(row=0, column=0, padx=10, pady=10)

# Graph section
graph_frame = tk.Frame(frame)
graph_frame.grid(row=0, column=0, padx=10, pady=10)

# Table section
table_frame = tk.Frame(frame)
table_frame.grid(row=0, column=1, padx=10, pady=10)

# Stock input section
input_frame = tk.Frame(root)
input_frame.grid(row=1, column=0, padx=10, pady=10)

stock_label = tk.Label(input_frame, text="Enter Stock Symbol:")
stock_label.grid(row=0, column=0, padx=5, pady=5)

stock_entry = tk.Entry(input_frame)
stock_entry.grid(row=0, column=1, padx=5, pady=5)

fetch_button = tk.Button(input_frame, text="Fetch Data", command=update_display)
fetch_button.grid(row=0, column=2, padx=5, pady=5)

buy_button = tk.Button(input_frame, text="Buy", command=buy_stock)
buy_button.grid(row=1, column=0, padx=5, pady=5)

sell_button = tk.Button(input_frame, text="Sell", command=sell_stock)
sell_button.grid(row=1, column=1, padx=5, pady=5)

exit_button = tk.Button(input_frame, text="Exit", command=on_exit)
exit_button.grid(row=1, column=2, padx=5, pady=5)

# Table Setup for Stock Data (Tab 1)
stock_data_tree = ttk.Treeview(table_frame, columns=("Time", "Price", "Suggestion"), show="headings")
stock_data_tree.heading("Time", text="Time")
stock_data_tree.heading("Price", text="Price ($)")
stock_data_tree.heading("Suggestion", text="Suggested Action")
stock_data_tree.pack(pady=10)
# Table Setup for Portfolio (Tab 1)
portfolio_tree = ttk.Treeview(table_frame, columns=("Symbol", "Quantity", "Price"), show="headings")
portfolio_tree.heading("Symbol", text="Stock Symbol")
portfolio_tree.heading("Quantity", text="Quantity")
portfolio_tree.heading("Price", text="Price ($)")
portfolio_tree.pack(pady=10)
# Table Setup for Transaction History (Tab 2)
transaction_history_tree = ttk.Treeview(tab2, columns=("Time", "Action", "Symbol", "Quantity", "Price"), show="headings")
transaction_history_tree.heading("Time", text="Time")
transaction_history_tree.heading("Action", text="Action")
transaction_history_tree.heading("Symbol", text="Stock Symbol")
transaction_history_tree.heading("Quantity", text="Quantity")
transaction_history_tree.heading("Price", text="Price ($)")
transaction_history_tree.pack(pady=10)
# Graph Setup
fig, ax = plt.subplots(figsize=(8,6))#CHANGE THE WINDOW SIZE HERE
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack()
root.mainloop()