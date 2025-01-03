from dotenv import load_dotenv
import boto3
import os
import csv
import time
import pandas as pd

load_dotenv()


AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
BUCKET_NAME = os.getenv('BUCKET_NAME')
S3_FILE_NAME = "kalshi-historical.csv"
LOCAL_FILE_NAME = "kalshi-hourly-data.csv"

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY,
                  aws_secret_access_key=AWS_SECRET_KEY,
                  region_name=AWS_REGION)


def download_file_from_s3():
    try:
        # Download the file
        local_file = "kalshi-historical.csv"  # Save the file locally with the same name
        s3.download_file(BUCKET_NAME, S3_FILE_NAME, local_file)
        print(f"Downloaded {S3_FILE_NAME} from {BUCKET_NAME} to {local_file}")
    except Exception as e:
        print(f"Error downloading file: {e}")

def merge_and_upload_to_s3():
    try:
        download_file_from_s3()
        # Load the historical data (which already has headers)
        historical_df = pd.read_csv('kalshi-historical.csv')
        
        # Load the hourly data without headers and assign column names manually
        hourly_column_names = ['time', 'currency', 'event_type', 'contract_type', 'strike_price', 'model_prediction', 'current_kalshi_price']
        hourly_df = pd.read_csv(LOCAL_FILE_NAME, header=None, names=hourly_column_names)
        
        # Merge the historical data and hourly data (concatenate them vertically)
        merged_df = pd.concat([historical_df, hourly_df], ignore_index=True)
        
        # Save the merged dataframe to the same file name (kalshi-historical.csv)
        merged_df.to_csv('kalshi-historical.csv', index=False)
        
        # Upload the merged CSV file back to S3 with the same name
        s3.upload_file('kalshi-historical.csv', BUCKET_NAME, S3_FILE_NAME)
        
        # Clear the local kalshi-hourly-data.csv so that it's ready for the next cycle
        with open(LOCAL_FILE_NAME, 'w') as f:
            f.truncate(0)  # Clears the content of the file
        # Clean up the temporary merged file
        os.remove('kalshi-historical.csv')
        
        print("Merged and uploaded data to S3 successfully. Cleared local hourly file")
    except Exception as e:
        print(f"Error during merge and upload: {e}")


def update_local_csv(timestamp, currency, event_type, contract_type, strike_price, model_pred, current_kalshi):
    row = [timestamp, currency, event_type, contract_type, strike_price, model_pred, current_kalshi]
    with open(LOCAL_FILE_NAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)     
        print(f"Row appended successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}")
