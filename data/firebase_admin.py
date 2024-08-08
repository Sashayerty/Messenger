import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db

class FirebaseAdmin():
    def __init__(self) -> None:
        self.cred = credentials.Certificate("api_keys/simplechat-39233-firebase-adminsdk-1e0ku-23879c078d.json")
        self.default_app = firebase_admin.initialize_app(self.cred, {
	        'databaseURL': 'https://simplechat-39233-default-rtdb.europe-west1.firebasedatabase.app/',
            'storageBucket' : 'storage-bucket-local-name'
	    })
        self.bucket = storage.bucket()

    def get_data(self, path_in_firebase):
        return db.reference(f'{path_in_firebase}').get()
    
    def add_data(self, path_in_firebase, data):
        db.reference(f'{path_in_firebase}').update(data)