import os

from firebase_admin import credentials

APP_NAME = "cami"
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
MODEL_GEMINI_2_0_PRO = "gemini-2.5-pro-preview-06-05"


DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")

USER_ID = os.environ.get("USER_ID", "octopus")


firebase_credentials = credentials.Certificate(
    os.environ.get("GOOGLE_FIREBASE_CREDENTIALS_PATH")
)
