import warnings
import logging
from dotenv import load_dotenv

def setup_env():
    warnings.filterwarnings("ignore")
    logging.basicConfig(level=logging.ERROR)
    load_dotenv()
