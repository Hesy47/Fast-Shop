from database import local_session


def get_db():
    db = local_session()

    try:
        yield db

    finally:
        db.close()
