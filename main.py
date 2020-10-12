import os

from slack_bot import create_app, db

app = create_app(os.environ.get("FLASK_ENV"))


@app.cli.command("init-db")
def init_db():
    print("current environment is", os.environ.get("FLASK_ENV"))
    y = input("do you want to continue (y/N)")

    if y == "y":
        db.create_all()


@app.cli.command("drop-db")
def init_db():
    print("current environment is", os.environ.get("FLASK_ENV"))
    y = input("do you want to continue (y/N)")

    if y == "y":
        db.drop_all()
