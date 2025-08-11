# 🏎️ F1 Weekend Race Notifier (AWS Lambda + SNS)

This AWS Lambda function checks the OpenF1 API (or a fallback list) for any Formula 1 race happening between today and the upcoming Sunday. If a race is found, it sends a notification via Amazon SNS.

## Features
- Fetches live 2025 F1 race data from [OpenF1 API](https://openf1.org)
- Falls back to static race list if API fails
- Sends alerts to SNS subscribers
- Deployable to AWS Lambda (Python 3.12)

## Tech Stack
- Python 3.12
- AWS Lambda
- Amazon SNS
- OpenF1 API
- requests

## Deployment
1. Install dependencies:
   ```bash
   pip install -r requirements.txt -t .
