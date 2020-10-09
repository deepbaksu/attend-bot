import os


def get_database_uri() -> str:
    db = os.environ.get("DB_URI")

    if db:
        print(db)
        return db

    print("using in-memory DB")
    return "sqlite:///:memory:"
