#!/usr/bin/env python3
# coding: utf-8

import  os
import gzip
import csv
import pandas as pd
import argparse
from sqlalchemy import create_engine
from time import time

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    csv_download = 'output.csv.gz'
    csv_name = 'output.csv.gz'
    #download the csv
    os.system(f"wget {url} -O {csv_name}")
    
    engine=create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    df=next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(0).to_sql(name=table_name, con=engine, if_exists='replace')
    df.to_sql(name=table_name, con=engine, if_exists='append')

    while True:
        t_start = time()
        try:        
            df=next(df_iter)
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            df.to_sql(name=table_name, con=engine, if_exists='append')
            t_end = time()
            print('inserted another chunk, took %.3f second' %(t_end-t_start)) 
        except StopIteration:
            break
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Ingest csv data to postgres')
    parser.add_argument('--user', help='username to postgres db')
    parser.add_argument('--password', help='password for postgres db')
    parser.add_argument('--host', help='host name to postgres db')
    parser.add_argument('--port', help='port number to connect to postgres db')
    parser.add_argument('--db', help='database name in postgres db')
    parser.add_argument('--table_name', help='Table Name in postgres db')
    parser.add_argument('--url', help='url to download the csv file')
    args = parser.parse_args()
    
    print(args)

    main(args)
    
    print("data load completed")

