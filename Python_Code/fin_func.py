import pandas as pd
import yfinance as yf
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text
from psycopg2.errors import UniqueViolation
import logging

# This document will contain the function required to run fin_software.

# Functions related to data acquisition

# The get_stock_data function, pulls data from yfinance (line2).
# It then removes the columns daily "High", "Low", "Adj Close," and daily "Volume".
# It adds in the column "daily_change", which measures the change in price over the course of the day.

def get_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    if not isinstance(symbol, str):
        raise TypeError("'symbol' must be a string representing a valid stock symbol")
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    try:
        stock_data = yf.download(symbol, start=start_date, end=end_date)
    except Exception as e:
        logging.error(f"Error downloading stock data: {e}")
        return None

    if stock_data.empty:
        logging.error(f"Error stock data received. Aborting further operations.")
        return None

    stock_data = stock_data.drop(columns=['High', 'Low', 'Adj Close', 'Volume'], errors='ignore', inplace=True)
    stock_data['daily_change'] = stock_data['Close'] - stock_data['Open']
    stock_data['symbol'] = symbol
    stock_data.reset_index(inplace=True)
    logging.info("Stock_data downloaded, High and Low columns removed, daily_change added")
    return stock_data


# Commodities data acquisition
def get_commodities_data(symbol, start_date, end_date):
    commodities_data = yf.download(symbol, start=start_date, end=end_date)
    commodities_data = commodities_data.drop(columns = ['High', 'Low', 'Adj Close', 'Volume'])
    commodities_data['daily_change'] = commodities_data['Close'] - commodities_data['Open']
    commodities_data['symbol'] = symbol
    commodities_data.reset_index(inplace = True)
    print("commodities_data downloaded, High and Low columns removed, daily_change added")
    return commodities_data


# Functions related to the database


######BELOW CODE NEEDED TO USE DATABASE FUNCTIONS#####
# Database connection details
#database = 'fin_data'
#user = 'stevengiallourakis'
#password = 'Birdman11!' # this might not be needed depenending on where you are connecting from.
#host = 'localhost'
#port =  '5433'
#connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
#engine = create_engine(connection_string)
######ABOVE CODE NEEDED TO USE DATABASE FUNCTIONS#####






# Add new data to database using data_to_db
# The code below uses engine, to make a connection to the database and allow for the use of sql commands.
# It then allows for the data to be copied from the  dataframe "df = stock_data" to the table specified.
# The code also handles error and duplicate entries.

def data_to_db(df, table_name, engine):
    try:
        with engine.begin() as connection:
            for index, row in df.iterrows():
                sql = text(f"""
                    INSERT INTO {table_name} ("Date", "Open", "Close", daily_change, symbol)
                    VALUES (:Date, :Open, :Close, :daily_change, :symbol)
                    ON CONFLICT (symbol, "Date") DO NOTHING
                """)
                connection.execute(sql, {
                    'Date': row['Date'],
                    'Open': row['Open'],
                    'Close': row['Close'],
                    'daily_change': row['daily_change'],
                    'symbol': row['symbol']
                })

        # df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        # print("Data successfully added to the database.")

    except UniqueViolation as e:
        print(f"Duplicate entry found for {symbol} on {data['date']}. Skipping insert.")
    except Exception as e:
        print(f"An error occurred while inserting data: {e}")





# Take csv data and load it into database
def csv_to_db(file_path):
    csv_df = pd.read_csv('file_path')
    return csv_df





# Functions related







