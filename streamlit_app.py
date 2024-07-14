import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

def run_strategy(start_date, end_date, selected_stock):
    # Define the path to the CSV file
    file_path = 'ndx100/' + selected_stock

    # Initialize an empty DataFrame to store filtered data
    filtered_data = pd.DataFrame()

    # Read and process data in chunks
    chunksize = 10000  # Adjust this size based on memory constraints
    for chunk in pd.read_csv(file_path, chunksize=chunksize, parse_dates=['DATE']):
        # Filter the chunk based on the date range
        chunk_filtered = chunk[(chunk['DATE'] >= start_date) & (chunk['DATE'] <= end_date)]
        filtered_data = pd.concat([filtered_data, chunk_filtered], ignore_index=True)

    # Calculate 50-day SMA
    filtered_data['Short_SMA'] = filtered_data['CLOSE'].rolling(window=50).mean()

    # Calculate 200-day SMA
    filtered_data['Long_SMA'] = filtered_data['CLOSE'].rolling(window=200).mean()

    # Find intersections
    filtered_data['Signal'] = 0  # Initialize a column to mark intersections
    for i in range(1, len(filtered_data)):
        try:
            if filtered_data.at[i, 'Short_SMA'] > filtered_data.at[i, 'Long_SMA'] and filtered_data.at[i - 1, 'Short_SMA'] <= filtered_data.at[i - 1, 'Long_SMA']:
                filtered_data.at[i, 'Signal'] = 1  # Upward crossover
            elif filtered_data.at[i, 'Short_SMA'] < filtered_data.at[i, 'Long_SMA'] and filtered_data.at[i - 1, 'Short_SMA'] >= filtered_data.at[i - 1, 'Long_SMA']:
                filtered_data.at[i, 'Signal'] = -1  # Downward crossover
        except KeyError:
            continue

    # Plot the data
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.plot(filtered_data['DATE'], filtered_data['Short_SMA'], label='50-day SMA', linestyle='--', color='blue')
    ax.plot(filtered_data['DATE'], filtered_data['Long_SMA'], label='200-day SMA', linestyle='--', color='green')
    ax.plot(filtered_data['DATE'], filtered_data['CLOSE'], label='Closing price', linestyle='-', color='black', linewidth=1)
    ax.fill_between(filtered_data['DATE'], filtered_data['Short_SMA'], filtered_data['Long_SMA'], where=filtered_data['Short_SMA'] >= filtered_data['Long_SMA'],
                    facecolor='green', interpolate=True, alpha=0.3)
    ax.fill_between(filtered_data['DATE'], filtered_data['Short_SMA'], filtered_data['Long_SMA'], where=filtered_data['Short_SMA'] < filtered_data['Long_SMA'],
                    facecolor='red', interpolate=True, alpha=0.3)
    upward_crossings = filtered_data[filtered_data['Signal'] == 1]
    downward_crossings = filtered_data[filtered_data['Signal'] == -1]
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
    directory = 'ndx100/ndx100'
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

