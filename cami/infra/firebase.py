import firebase_admin
from firebase_admin import credentials, firestore_async

cred = credentials.Certificate('./firebase.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cami-v2.asia-south2.firebaseio.com'
})

db = firestore_async.client()
