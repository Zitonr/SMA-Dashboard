import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

def run_strategy(start_date, end_date, selected_stock):
    # Read the CSV file for the selected stock
    df = pd.read_csv('ndx100/' + selected_stock)

    # Convert 'DATE' column to datetime format
    df['DATE'] = pd.to_datetime(df['DATE'])

    # Calculate 50-day SMA
    df['Short_SMA'] = df['CLOSE'].rolling(window=50).mean()

    # Calculate 200-day SMA
    df['Long_SMA'] = df['CLOSE'].rolling(window=200).mean()

    # Debug: Print date range
    st.write(f"Filtering data from {start_date} to {end_date}")

    # Filter dataframe based on user input date range
    df = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]

    # Debug: Print the filtered dataframe
    # st.write(df.head())  # Commented out to remove the table display

    # Find intersections
    df['Signal'] = 0  # Initialize a column to mark intersections
    for i in range(1, len(df)):
        try:
            if df.at[i, 'Short_SMA'] > df.at[i, 'Long_SMA'] and df.at[i - 1, 'Short_SMA'] <= df.at[i - 1, 'Long_SMA']:
                df.at[i, 'Signal'] = 1  # Upward crossover
            elif df.at[i, 'Short_SMA'] < df.at[i, 'Long_SMA'] and df.at[i - 1, 'Short_SMA'] >= df.at[i - 1, 'Long_SMA']:
                df.at[i, 'Signal'] = -1  # Downward crossover
        except KeyError:
            continue

    # Plot the data
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(df['DATE'], df['Short_SMA'], label='50-day SMA', linestyle='--', color='blue')
    ax.plot(df['DATE'], df['Long_SMA'], label='200-day SMA', linestyle='--', color='green')
    ax.plot(df['DATE'], df['CLOSE'], label='Closing price', linestyle='-', color='black', linewidth=1)
    ax.fill_between(df['DATE'], df['Short_SMA'], df['Long_SMA'], where=df['Short_SMA'] >= df['Long_SMA'],
                    facecolor='green', interpolate=True, alpha=0.3)
    ax.fill_between(df['DATE'], df['Short_SMA'], df['Long_SMA'], where=df['Short_SMA'] < df['Long_SMA'],
                    facecolor='red', interpolate=True, alpha=0.3)
    upward_crossings = df[df['Signal'] == 1]
    downward_crossings = df[df['Signal'] == -1]
    ax.scatter(upward_crossings['DATE'], upward_crossings['Short_SMA'], marker='^', color='green',
               label='Upward crossover')
    ax.scatter(downward_crossings['DATE'], downward_crossings['Short_SMA'], marker='v', color='red',
               label='Downward crossover')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title(f"{os.path.splitext(selected_stock)[0]} Stock prices")
    ax.legend()

    return fig

# Streamlit app
def main():
    st.title('Stock Trading Strategy Simulation')

    # User input for date range
    start_date = st.date_input('Enter the start date:')
    end_date = st.date_input('Enter the end date:')

    # List available stocks
    directory = 'ndx100'
    stocks = [os.fsdecode(file) for file in os.listdir(directory) if file.endswith('.csv')]
    selected_stock = st.selectbox('Select a stock:', stocks)

    if st.button('Run Strategy'):
        st.write(f"Running strategy on {selected_stock} from {start_date} to {end_date}...")

        # Convert date inputs to string format
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        fig = run_strategy(start_date_str, end_date_str, selected_stock)
        st.pyplot(fig)

if __name__ == "__main__":
    main()
