import pandas as pd
import requests
import os
import timezone
from datetime import date
from rich import print
from configparser import ConfigParser

# Define the path to the CSV file
xlsx_file_path = os.path.expanduser("interest.xlsx")

# Define the API endpoint and headers
headers = {
    "Accept": "application/vnd.mambu.v2+json"
}
mambu_url = ""

# Load configuration from config.ini
config = ConfigParser()
config.read('config.ini')

# Retrieve API URLs and authorization tokens from the config file
reevo_url = config.get('mambu', 'reevo_url')
ccb_url = config.get('mambu', 'ccb_url')
reevo_auth = config.get('mambu', 'reevo_auth')
ccb_auth = config.get('mambu', 'ccb_auth')

def process_xlsx(file_path):
    try:
        data = pd.read_excel(file_path)
        if data[data['sent'].isna()].empty:
            print("[bold yellow]No rows to process.[/bold yellow]")
            return
        for _, row in data[data['sent'].isna()].iterrows():
                # Prepare the payload for the API call
                account_number = row["account_number"]
                if row["brand"] == "Reevo":
                    mambu_url = reevo_url
                    headers["Authorization"] = "Basic " + reevo_auth
                elif row["brand"] == "CCB":
                    mambu_url = ccb_url
                    headers["Authorization"] = "Basic " + ccb_auth
                mambu_date = timezone.timezone.is_dst(targetdate=row["date"].strftime("%Y-%m-%d"))
                payload = {
                    "notes": "interest rate amendment as per mid-office",
                    "interestRate": float(row["interest_rate"]) if not pd.isna(row["interest_rate"]) else None,
                    "valueDate": mambu_date
                }
                api_url = f"{mambu_url}{account_number}" + ":changeInterestRate"
                print(api_url)
                print(payload)
                response = requests.post(api_url, json=payload, headers=headers)
                # Check the response
                if response.status_code == 204:
                    data.loc[row.name, 'sent'] = pd.Timestamp.now()
                    data.to_excel(file_path, index=False)
                    print(f"""[bold green]Successfully processed record: {row["account_number"]}[/bold green]""")
                else:
                    print(f"""[bold red]Failed to process record: {row["account_number"]}, Status Code: {response.status_code}, Response: {response.text}[/bold red]""")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
process_xlsx(xlsx_file_path)