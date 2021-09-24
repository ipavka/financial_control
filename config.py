import os

from dotenv import load_dotenv


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
PASSWORD_SALT = os.getenv("PASSWORD_SALT")
