import pandas as pd
import yfinance as yf
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text
from psycopg2.errors import UniqueViolation
import logging
from scipy.stats import pearsonr


# This document will contain the function required to run fin_software.

# Functions related to data acquisition from database

# The get_stock_data function, pulls data from yfinance (line2).
# It then removes the columns daily "High", "Low", "Adj Close," and daily "Volume".
# It adds in the column "daily_change", which measures the change in price over the course of the day.

def get_stock_data(stock_symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    if not isinstance(stock_symbol, str):
        raise TypeError("'stock_symbol' must be a string representing a valid stock symbol")
    try:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    except Exception as e:
        logging.error(f"Error converting dates to datetime: {e}")
        return None
    try:
        stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
    except Exception as e:
        logging.error(f"Error downloading stock data: {e}")
        return None

    if stock_data.empty:
        logging.error(f"Error stock data received. Aborting further operations.")
        return None

    # Drop unnecessary columns
    stock_data = stock_data.drop(columns=['High', 'Low', 'Adj Close', 'Volume'], errors='ignore')

    # Calculate daily change and percent change
    stock_data['daily_change'] = stock_data['Close'] - stock_data['Open']
    stock_data['percent_change'] = (
            ((stock_data['Close'] - stock_data['Open']) / stock_data['Open']) * 100)

    # Add the stock symbol column
    stock_data['stock_symbol'] = stock_symbol

    
    stock_data.reset_index(inplace=True)
    logging.info("Stock_data downloaded, High and Low columns removed, daily_change added")
    return stock_data


# Commodities data acquisition
def get_commodity_data(commodity_symbol, start_date, end_date) -> pd.DataFrame:
    if not isinstance(commodity_symbol, str):
        raise TypeError("'commodity_symbol' must be a string representing a valid commodity symbol")
    try:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    except Exception as e:
        logging.error(f"Error converting dates to datetime: {e}")
        return None
    try:
        commodity_data = yf.download(commodity_symbol, start=start_date, end=end_date)
        if commodity_data.empty:
            logging.warning(f"Error commodity data received. Aborting further operations.")
            return None
    except Exception as e:
        logging.error(f"Error downloading commodity data: {e}")
        return None

    commodity_data.drop(columns=['High', 'Low', 'Adj Close', 'Volume'], inplace=True)
    commodity_data['daily_change'] = commodity_data['Close'] - commodity_data['Open']
    commodity_data['percent_change'] = (
            ((commodity_data['Close'] - commodity_data['Open']) / commodity_data['Open']) * 100)
    commodity_data['commodity_symbol'] = commodity_symbol
    commodity_data.reset_index(inplace=True)
    logging.info("commodity_data downloaded, High and Low columns removed, daily_change added")
    return commodity_data


# Functions related to the database


######BELOW CODE NEEDED TO USE DATABASE FUNCTIONS#####
# Database connection details
# database = 'fin_data'
# user = 'stevengiallourakis'
# password = 'Birdman11!' # this might not be needed depenending on where you are connecting from.
# host = 'localhost'
# port =  '5433'
# connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
# engine = create_engine(connection_string)
######ABOVE CODE NEEDED TO USE DATABASE FUNCTIONS#####


# Add new data to database using data_to_db
# The code below uses engine, to make a connection to the database and allow for the use of sql commands.
# It then allows for the data to be copied from the  dataframe "df = stock_data" to the table specified.
# The code also handles error and duplicate entries.


# Add new data to database

def data_to_db(df, table_name, engine):
    try:
        with engine.begin() as connection:
            for index, row in df.iterrows():
                sql = text(f"""
                    INSERT INTO {table_name} ("Date", "Open", "Close", daily_change, percent_change, symbol)
                    VALUES (:Date, :Open, :Close, :daily_change, :symbol)
                    ON CONFLICT (symbol, "Date") DO NOTHING
                """)
                connection.execute(sql, {
                    'Date': row['Date'],
                    'Open': row['Open'],
                    'Close': row['Close'],
                    'daily_change': row['daily_change'],
                    'percent_change': row['percent_change'],
                    'symbol': row['symbol']
                })
        

        
        #df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        #print("Data successfully added to the database.")
    
    except UniqueViolation as e:
        print(f"Duplicate entry found for {stock_symbol} on {data['date']}. Skipping insert.")
    except Exception as e:
        print(f"An error occurred while inserting data: {e}")
    

# Take csv data and load it into database
def csv_to_db(file_path):
    csv_df = pd.read_csv('file_path')
    return csv_df


# check_stock_symbol_exists examines whether a company or stock symbol is contained in the table company_list.
# this must be done before attemping to pull data from dail_stock_prices for analysis.

def does_stock_symbol_exist(engine, stock_symbol) -> bool:
    query = "SELECT EXISTS(SELECT 1 FROM company_list WHERE stock_symbol = %s"
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {'stock_symbol': stock_symbol})
            return result.scalar()
    except Exception as e:
        logging.error(f"Error occurred: {e}")


# Function to fetch stock data from daily_stock_prices


# Functions related to statistical analysis

def fetch_stock_data(engine, stock_symbol) -> pd.DataFrame:
    try:
        query = """
        SELECT date, close
        FROM daily_stock_prices
        WHERE stock_symbol = %s
        ORDER BY date    
        """
        if not isinstance(stock_symbol, str):
            raise ValueError("Stock symbol must be a string")
        with engine.connect() as conn:
            return pd.read_sql_query(query, conn, params={"stock_symbol": stock_symbol})
    except Exception as e:
        logging.error(f"Error fetching stock data: {e}")


def pearson_analysis(main_stock: str, other_stocks: dict, start_date: str, end_date: str) -> pd.DataFrame:
    main_stock_df = fetch_stock_data(main_stock, start_date, end_date)

    correlation_results - {}
    for stock, stock_label in other_stocks.items():
        comparison_stock_df = fetch_stock_data(stock, start_date, end_date)
        combined_df = pd.merge(main_stock_df, comparison_stock_df, on='date', how='inner', suffixes=('_main', '_comp'))

        # Compute Pearson Correlation
        correlation = combined_df['close_price_main'].corr(combined_df['close_price_comp'], method='pearson')
        correlation_results[stock_label] = correlation

    return correlation_results





# Code Creates
