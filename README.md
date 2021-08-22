# attend-bot

![CI](https://github.com/deepbaksu/attend-bot/workflows/CI/badge.svg)
![Website](https://img.shields.io/website?down_message=bot%20is%20offline&up_message=bot%20is%20online&url=https%3A%2F%2Fslackattend.herokuapp.com%2Fhealthcheck)

슬랙 출첵 봇 만드는 채널입니다.

## How to test

0. Install dependencies using `pipenv`.

   ```bash
   pipenv install --dev
   ```

1. Run postgres locally
   ```bash
   ./run_postgres.sh
   ```
2. Run development server.

   ```bash
   pipenv run start
   ```

   > **TIP:** you can use ngrok and use that by creating a temporary command in https://api.slack.com/apps/A01BHLV79UZ/slash-commands.

3. Run `pytest`.
   ```bash
   pipenv run pytest
   ```
4. Run `black` and `isort` before committing your changes.
   ```bash
   pipenv run black . && isort .
   ```
