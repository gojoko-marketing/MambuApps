import boto3
import sys
import botocore.exceptions

# Use AWS profile
#aws sso login --profile CollectionsAdmin-755177498602
session = boto3.Session(profile_name="CollectionsAdmin-755177498602")
region_name = "eu-west-1"
secret_name = "prod/mambu/ccb"

# Create the client
client = session.client(
    service_name='secretsmanager',
    region_name=region_name
)

try:
    response = client.get_secret_value(SecretId=secret_name)
    secret = response.get("SecretString", "<No string secret found>")
    print(f"Secret value:\n{secret}")
except botocore.exceptions.ClientError as e:
    print(f"Error retrieving secret: {e.response['Error']['Message']}")
