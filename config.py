import logging
import os

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)
logger = logging.getLogger('api')

load_dotenv()

QUESTDB_HOST = os.getenv('QUESTDB_HOST')
QUESTDB_PORT = int(os.getenv('QUESTDB_PORT'))
QUESTDB_USER = os.getenv('QUESTDB_USER')
QUESTDB_PASSWORD = os.getenv('QUESTDB_PASSWORD')
QUESTDB_DATABASE = os.getenv('QUESTDB_DATABASE')