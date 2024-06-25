import json
import requests
from bs4 import BeautifulSoup
import csv
import boto3
from datetime import datetime, timedelta

def lambda_handler(event, context):
    # get date as format 'YY-MM-DD'
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

    # function to fetch data in URL
    def fetch_data(url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # check whether the response was returned
            return response
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # HTTP error
            return None
        except Exception as err:
            print(f'Other error occurred: {err}')  # Other error
            return None

    # URL of yesterday
    url = f'https://www.oricon.co.jp/rank/js/d/{yesterday}/'

    # fetch data from URL
    response = fetch_data(url)

    # if URL exists, parse HTML with BS4
    if response is not None:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # extract class="box-rank-entry"
        rank_entries = soup.find_all(class_='box-rank-entry')
        
        # Create CSV content
        csv_content = "Status,Title,Name\n"
        
        for entry in rank_entries:
            # get ranking fluctuations
            status_tag = entry.find('p', class_='status')
            status = status_tag.text.strip() if status_tag else 'N/A'
            
            # get single-title
            title_tag = entry.find('h2', class_='title')
            title = title_tag.text.strip() if title_tag else 'N/A'
            
            # get artist name
            name_tag = entry.find('p', class_='name')
            name = name_tag.text.strip() if name_tag else 'N/A'
            
            # Add row to CSV content
            csv_content += f"{status},{title},{name}\n"
        
        # upload to S3
        s3 = boto3.client('s3')
        bucket_name = "scrape-portfolio"
        now = datetime.now().strftime("%Y%m%d") 
        file_name = f"{now}.csv"
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_content)
        
        return {
            'statusCode': 200,
            'body': json.dumps('CSV file created and uploaded to S3')
        }
                
    else:
        return {
            'statusCode': 500,
            'body': json.dumps('Could not retrieve data.')
        }