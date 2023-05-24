import os

# AWS variables
app_environment = os.environ.get('APP_ENVIRONMENT')
aws_account_tld = os.environ.get('APP_DNS_DOMAIN')[:-1]
stack_name = 'cloudchirp'
s3_bucket_name = f'{app_environment}-{stack_name}.{aws_account_tld}'

# Site locations - sorted by abbreviation name
site_locations = [
    {'site_name': 'The Trent House',
     'site_address': '1234 Rockford Place',
     'site_city': 'Rockford, Michigan',
     'site_abbv': 'RFMI'},
    {'site_name': 'The Fredrick House',
     'site_address': '1 Black Crayon Ave',
     'site_city': 'GR, Michigan',
     'site_abbv': 'GRMI'}
]

# What filenames to create
file_names = ['During_Hours', 'After_Hours', 'During_Hours_No_Answer']
