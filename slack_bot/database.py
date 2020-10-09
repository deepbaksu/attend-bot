import os


def get_database_uri() -> str:
    db = os.environ.get("DATABASE_URL")

    if db:
        print(db)
        return db

    print("using in-memory DB")
    return "sqlite:///:memory:"
