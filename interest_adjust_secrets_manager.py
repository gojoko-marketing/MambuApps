import pandas as pd
import requests
import os
import timezone
import boto3
from botocore.exceptions import ClientError
from datetime import date
from rich import print
import json
from configparser import ConfigParser
import subprocess

# Ensure AWS SSO login is performed
subprocess.run(["aws", "sso", "login", "--profile", "CollectionsAdmin-755177498602"], check=True)

# Define the path to the CSV file
xlsx_file_path = os.path.expanduser("interest.xlsx")

# Define the API endpoint and headers
headers = {"Accept": "application/vnd.mambu.v2+json"}
mambu_url = ""
# Load configuration from config.ini
config = ConfigParser()
config.read('config.ini')
reevo_url = config.get('mambu', 'reevo_prod_url')
ccb_url = config.get('mambu', 'ccb_prod_url')

def get_secret(brand):
    region_name = "eu-west-1"
    if brand == "Reevo":
        secret_name = "prod/mambu/reevo"
    elif brand == "CCB":
        secret_name = "prod/mambu/ccb"

    # Create Secrets Manager client
    session = boto3.Session(profile_name="CollectionsAdmin-755177498602", region_name=region_name)
    client = session.client("secretsmanager")

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    return secret

def process_xlsx(file_path):
    try:
        data = pd.read_excel(file_path)
        if data[data['sent'].isna()].empty:
            print("[bold yellow]No rows to process.[/bold yellow]")
            return
        for _, row in data[data['sent'].isna()].iterrows():
                # Prepare the payload for the API call
                account_number = row["account_number"]
                if row["brand"] == "Reevo": #also add access token into headers
                    mambu_url = reevo_url
                    secret = get_secret("Reevo")
                elif row["brand"] == "CCB":
                    mambu_url = ccb_url
                    secret = get_secret("CCB")
                secret = json.loads(secret)
                secret = secret["access_token"]
                headers["Authorization"] = "Basic " + secret
                mambu_date = timezone.timezone.is_dst(targetdate=row["date"].strftime("%Y-%m-%d"))
                payload = {
                    "notes": "mid-office interest rate amendment",
                    "interestRate": float(row["interest_rate"]) if not pd.isna(row["interest_rate"]) else None,
                    "valueDate": mambu_date
                }
                api_url = f"{mambu_url}{account_number}" + ":changeInterestRate"
                response = requests.post(api_url, json=payload, headers=headers)
                # Check the response
                if response.status_code == 204:
                    data.loc[row.name, 'sent'] = pd.Timestamp.now()
                    data.to_excel(file_path, index=False)
                    print(f"""[bold green]Successfully processed record ({row["brand"]}): {row["account_number"]}[/bold green]""")
                else:
                    print(f"""[bold red]Failed to process record ({row["brand"]}): {row["account_number"]}, Status Code: {response.status_code}, Response: {response.text}[/bold red]""")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"[bold red]An error occurred: {e}[/bold red]")

# Run the function
process_xlsx(xlsx_file_path)