import logging
import os

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)
logger = logging.getLogger('api')

load_dotenv()

QUESTDB_HOST = os.getenv('QUESTDB_HOST', '127.0.0.1')
QUESTDB_PORT = int(os.getenv('QUESTDB_PORT', '8812'))
QUESTDB_USER = os.getenv('QUESTDB_USER', 'admin')
QUESTDB_PASSWORD = os.getenv('QUESTDB_PASSWORD', 'quest')
QUESTDB_DATABASE = os.getenv('QUESTDB_DATABASE', 'qdb')