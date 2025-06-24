from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from config import *


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=QUESTDB_HOST,
            port=QUESTDB_PORT,
            user=QUESTDB_USER,
            password=QUESTDB_PASSWORD,
            database=QUESTDB_DATABASE,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"failed to connect to QuestDB: {e}")
        raise

def parse_time(time_str: str) -> datetime:
    formats = [
        ('%Y-%m-%d %H:%M:%S', lambda dt: dt),
        ('%Y-%m-%d %H:%M', lambda dt: dt.replace(second=0)),
        ('%Y-%m-%d %H', lambda dt: dt.replace(minute=0, second=0)),
        ('%Y-%m-%d', lambda dt: dt.replace(hour=0, minute=0, second=0))
    ]
    for fmt, transform in formats:
        try:
            dt = datetime.strptime(time_str, fmt)
            return transform(dt)
        except ValueError:
            continue
    raise ValueError(f"invalid time format: {time_str}. Expected YYYY-MM-DD [HH[:MM[:SS]]]")