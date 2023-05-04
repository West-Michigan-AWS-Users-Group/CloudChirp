# CloudChirp

Text-to-Speech Solution on AWS with Polly, CloudFront, and S3


### App deployment

1. Clone this repo.
2. Checkout your branch name. The branch name is used to create a unique stack and environment for deployment.
3. Install your requirements
```shell
pip3 install -r ./app/requirements.txt
```
4. Create .env file and populate the following variables (note the trailing dot on the dns domain):
```
AWS_ACCOUNT_NUMBER=123456789123
AWS_ACCOUNT_NAME=account-name
AWS_DEFAULT_PROFILE=account-profile
APP_DNS_DOMAIN=example.domain.
```
5. Generate your Cloudformation template
```shell
python3 cloudformation/template.py
```
6. Deploy your CloudFormation stack
```shell
ENVIRONMENT=$(git rev-parse --abbrev-ref HEAD)
source .env && aws cloudformation deploy --template-file cloudformation/$ENVIRONMENT-template.json --stack-name $ENVIRONMENT-cloudchirp --region us-east-1 --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```
7. Ensure your ACM validation completes. AWS certificate manager will require you to validate your domain. If hosted in Route53 this is a 1 click deployment.
![acm-screenshot.png](acm-screenshot.png)
8. Fetch your aws access keys from the stack outputs and store Github actions secrets as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
9. You will now need to configure your Dockerhub credentials `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` for CI.
10. Re-run Actions to build and populate the files.