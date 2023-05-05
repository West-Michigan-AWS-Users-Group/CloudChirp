import os
from dotenv import load_dotenv
load_dotenv('../.env')

# AWS variables
aws_account_name = os.environ.get('AWS_ACCOUNT_NAME')
app_environment = os.environ.get('APP_ENVIRONMENT')
aws_account_tld = os.environ.get('APP_DNS_DOMAIN')
stack_name = 'cloudchirp'
s3_bucket_name = f'{app_environment}-{stack_name}.{aws_account_name}.{aws_account_tld}'

# Site locations - sorted by abbreviation name
site_locations = [
    {'site_name': 'The Factory',
     'site_address': '77 Monroe Center St NW Suite 600',
     'site_city': 'Grand Rapids, Michigan',
     'site_abbv': 'GRMI'}
]

# What filenames to create
file_names = ['During_Hours', 'After_Hours', 'During_Hours_No_Answer']
