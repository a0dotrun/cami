import firebase_admin

from cami.config import firebase_credentials

firebase_admin.initialize_app(firebase_credentials)
