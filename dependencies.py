from database import local_session
from contextlib import contextmanager


def get_db_fast():
    db = local_session()

    try:
        yield db

    finally:
        db.close()


@contextmanager
def get_db_python():
    db = local_session()

    try:
        yield db

    finally:
        db.close()
