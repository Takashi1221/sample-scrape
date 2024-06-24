import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta

# get date as format'YY-MM-DD'
today = datetime.now().strftime('%Y-%m-%d')
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

# URL of today
url_today = f'https://www.oricon.co.jp/rank/js/d/{today}/'

# fetch data from today URL
response = fetch_data(url_today)

# except today URL is None, fetch data from yesterday URL
if response is None:
    url_yesterday = f'https://www.oricon.co.jp/rank/js/d/{yesterday}/'
    response = fetch_data(url_yesterday)

# if URL is exist, parse HTML with BS4
if response is not None:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # extract class="box-rank-entry"
    rank_entries = soup.find_all(class_='box-rank-entry')
    
    # Open a CSV file to write
    with open('ranking.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Status', 'Title', 'Name'])
        
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
            
            # Write the row to CSV
            writer.writerow([status, title, name])
            
else:
    print("Could not retrieve data.")