#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path

import awacs.aws as awacs
import awacs.polly as awacs_polly
import awacs.s3 as awacs_s3
import troposphere.cloudfront as cf
import troposphere.iam as iam
import troposphere.s3 as s3
from dotenv import load_dotenv
from troposphere import GetAtt, Join, Output, Ref, Select, Split, Tags, Template
from troposphere.certificatemanager import Certificate, DomainValidationOption
from troposphere.route53 import AliasTarget, RecordSetType


# Function that saves the file , but makes sure it exists first.
def save_to_file(template, environment):
    settings_file_path = f'./cloudformation/{environment}-template.json'
    # Create settings file if it doesn't exist:
    settings_file = Path(settings_file_path)
    if settings_file.is_file():
        with open(settings_file_path, 'w+') as outfile:
            json.dump(template, outfile, indent=2)
    else:
        with open(settings_file_path, 'a'):
            os.utime(settings_file_path, None)
        with open(settings_file_path, 'w+') as outfile:
            json.dump(template, outfile, indent=2)


# load repo .env file
load_dotenv()

# Configuration Variables
app_group = 'cloudchirp'.capitalize()
app_group_l = app_group.lower()
app_group_ansi = app_group_l.replace('-', '')
stack_description = 'Cloudchirp Automation and related resources'

# AWS region/account vars
app_region = 'us-east-1'
aws_account_name = os.environ.get('AWS_ACCOUNT_NAME')
aws_account_number = os.environ.get('AWS_ACCOUNT_NUMBER')

# Branch to env mapping
branch_env_mapping = {
    'main': 'production',
    'develop': 'develop'
}
result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE)
branch_name = result.stdout.decode().strip()
try:
    app_environment = branch_env_mapping[branch_name]
except KeyError as e:
    app_environment = 'undefined'
    print('No branch mapping found')

# CloudFront vars
dns_domain = os.environ.get('APP_DNS_DOMAIN')
cfront_zone_id = 'Z2FDTNDATAQYW2'
custom_origin_id = f'{app_environment}-{app_group_l}'
app_dns_domain = f'{app_environment}-{app_group_l}.{dns_domain}'[:-1]
max_ttl = 31536000
default_ttl = 86400

# S3
bucket_name = app_dns_domain

# Pull In Tags
default_tags = Tags(Service=app_group) + \
               Tags(ExtendedName=f'{app_environment}-{app_region}-{app_group_l}')

# Prepare Template
t = Template()
t.set_description(f'{app_environment}: {aws_account_name} - {stack_description}')

saCloudchirpUser = t.add_resource(iam.User(
    'saCloudchirpUser',
))

saCloudchirpKeys = t.add_resource(iam.AccessKey(
    'saCloudchirpKeys',
    Status='Active',
    UserName=Ref(saCloudchirpUser)
))

# Don't do this in a normal production environment! This will output your keys in plain text in a CFN stack output.
t.add_output([
    Output(
        'saCloudchirpKeyId',
        Description='CloudChirp AccessKeyId',
        Value=Ref(saCloudchirpKeys),
    ),
    Output(
        'saCloudchirpSecretAccessKey',
        Description='CloudChirp SecretAccessKey',
        Value=GetAtt(saCloudchirpKeys, 'SecretAccessKey'),
    ),
])

saCloudchirpAutomationPolicy = t.add_resource(iam.PolicyType(
    'saCloudchirpAutomationPolicy',
    PolicyName=f'{aws_account_name}-{app_group_l}-cloudchirp-access',
    Users=[Ref('saCloudchirpUser')],
    PolicyDocument={
        'Statement': [
            awacs.Statement(
                Effect=awacs.Allow,
                Action=[
                    awacs_s3.GetBucketLocation,
                    awacs_s3.GetObject,
                    awacs_s3.GetObjectVersion,
                    awacs_s3.GetObjectAcl,
                    awacs_s3.ListBucket,
                    awacs_s3.ListBucketMultipartUploads,
                    awacs_s3.ListMultipartUploadParts,
                    awacs_s3.AbortMultipartUpload,
                    awacs_s3.PutObject,
                    awacs_s3.PutObjectAcl,
                    awacs_s3.RestoreObject,
                    awacs_s3.GetLifecycleConfiguration,
                    awacs_s3.DeleteObject,
                    awacs_s3.DeleteObjectVersion,
                    awacs_s3.GetBucketLocation,
                    awacs_s3.ListBucket,
                ],
                Resource=[
                    awacs_s3.ARN(f'{bucket_name}'),
                    awacs_s3.ARN(f'{bucket_name}*'),
                    awacs_s3.ARN(f'{bucket_name}/*')
                ],
            ),
            awacs.Statement(
                Effect=awacs.Allow,
                Action=[awacs_polly.Action('*')],
                Resource=['*'],
            )
        ]
    },
))

# Provision certificate for CDN
cdnCertificate = t.add_resource(Certificate(
    'cdnCertificate',
    DomainName=app_dns_domain,
    DomainValidationOptions=[DomainValidationOption(
        DomainName=app_dns_domain,
        ValidationDomain=dns_domain[:-1]
    )],
    ValidationMethod='DNS',
    Tags=default_tags + Tags(Name=f'{app_environment}-{app_group_l}')
))

cdnDistribution = t.add_resource(cf.Distribution(
    'cdnDistribution',
    DistributionConfig=cf.DistributionConfig(
        Comment=f'{app_environment} - {app_dns_domain}',
        Enabled=True,
        PriceClass='PriceClass_All',
        HttpVersion='http2',
        Origins=[
            cf.Origin(
                Id=custom_origin_id,
                # Retrieve the URL from the bucket without the http:// returned value
                DomainName=Select(1, Split('//', GetAtt('bucket', 'WebsiteURL'))),
                CustomOriginConfig=cf.CustomOriginConfig(
                    HTTPPort=80,
                    HTTPSPort=443,
                    OriginProtocolPolicy='http-only',
                    OriginSSLProtocols=['TLSv1.2'],
                )
            )
        ],
        Aliases=[app_dns_domain],
        ViewerCertificate=cf.ViewerCertificate(
            AcmCertificateArn=Ref(cdnCertificate),
            SslSupportMethod='sni-only',
            MinimumProtocolVersion='TLSv1.2_2018',
        ),
        DefaultCacheBehavior=cf.DefaultCacheBehavior(
            AllowedMethods=['GET', 'HEAD', 'OPTIONS'],
            CachedMethods=['GET', 'HEAD'],
            ViewerProtocolPolicy='redirect-to-https',
            TargetOriginId=custom_origin_id,
            ForwardedValues=cf.ForwardedValues(
                Headers=[
                    'Accept-Encoding'
                ],
                QueryString=True,
            ),
            MinTTL=0,
            MaxTTL=max_ttl,
            DefaultTTL=default_ttl,
            SmoothStreaming=False,
            Compress=True
        ),
        CustomErrorResponses=[
            cf.CustomErrorResponse(
                ErrorCachingMinTTL='0',
                ErrorCode='403',
            ),
            cf.CustomErrorResponse(
                ErrorCachingMinTTL='0',
                ErrorCode='404',
            ),
            cf.CustomErrorResponse(
                ErrorCachingMinTTL='0',
                ErrorCode='500',
            ),
            cf.CustomErrorResponse(
                ErrorCachingMinTTL='0',
                ErrorCode='501',
            ),
            cf.CustomErrorResponse(
                ErrorCachingMinTTL='0',
                ErrorCode='502',
            ),
            cf.CustomErrorResponse(
                ErrorCachingMinTTL='0',
                ErrorCode='503',
            ),
            cf.CustomErrorResponse(
                ErrorCachingMinTTL='0',
                ErrorCode='504',
            ),
        ],
    ),
    Tags=default_tags
))

bucket = t.add_resource(s3.Bucket(
    'bucket',
    BucketName=app_dns_domain,
    Tags=default_tags,
    WebsiteConfiguration=(s3.WebsiteConfiguration(
        IndexDocument='index.html'
    )),
    PublicAccessBlockConfiguration=s3.PublicAccessBlockConfiguration(
            BlockPublicAcls=False,
            BlockPublicPolicy=False,
            IgnorePublicAcls=False,
            RestrictPublicBuckets=False,
    ),
    OwnershipControls=s3.OwnershipControls(
        Rules=[s3.OwnershipControlsRule(ObjectOwnership='ObjectWriter')]
    )
))

# Provision the distribution origin access id to allow access to the bucket via CloudFront
cfoaid = t.add_resource(cf.CloudFrontOriginAccessIdentity(
    'cfoaid',
    CloudFrontOriginAccessIdentityConfig=cf.CloudFrontOriginAccessIdentityConfig(
        Comment=f'{app_dns_domain} origin access id'
    )
))

# Provision the bucket policy to restrict public viewing through the above OID
s3bucketpolicy = t.add_resource(s3.BucketPolicy(
    's3bucketpolicy',
    Bucket=Ref('bucket'),
    PolicyDocument={
        'Version': '2012-10-17',
        'Statement': {
            'Sid': 'AllowCloudFrontServicePrincipalReadOnly',
            'Effect': 'Allow',
            'Principal': {
                'Service': 'cloudfront.amazonaws.com'
            },
            'Action': 's3:GetObject',
            'Resource': f'arn:aws:s3:::{bucket_name}/*',
            'Condition': {
                'StringEquals': {
                    'AWS:SourceArn': Join('', [f'arn:aws:cloudfront::{aws_account_number}:distribution/',
                                               Ref('cdnDistribution')])
                }
            }
        }
    }
))

cdnARecord = t.add_resource(RecordSetType(
    'cdnARecord',
    HostedZoneName=dns_domain,
    Comment=f'{app_dns_domain} domain record',
    Name=app_dns_domain,
    Type='A',
    AliasTarget=AliasTarget(
        HostedZoneId=cfront_zone_id,
        DNSName=GetAtt(cdnDistribution, 'DomainName')
    )
))

t.add_output([
    Output(
        'BucketName',
        Value=Ref(bucket),
        Description=f'Name of S3 bucket for {app_group}'
    ),
    Output(
        'CDNDomainOutput',
        Description='Domain for CDN',
        Value=GetAtt(cdnDistribution, 'DomainName'),
    ),
    Output(
        'AppDomainOutput',
        Description='App user URL',
        Value=app_dns_domain,
    )
])

# Load the data into a json object
json_data = json.loads(t.to_json())

# Save the file to disk
save_to_file(json_data, app_environment)
