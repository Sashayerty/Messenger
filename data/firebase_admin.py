import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db

class FirebaseAdmin():
    def __init__(self) -> None:
        self.cred = credentials.Certificate("api_keys/simplechat-39233-firebase-adminsdk-1e0ku-23879c078d.json")
        self.default_app = firebase_admin.initialize_app(self.cred, {
	        'databaseURL': 'https://simplechat-39233-default-rtdb.europe-west1.firebasedatabase.app/',
            'storageBucket' : 'simplechat-39233.appspot.com'
	    })
        self.bucket = storage.bucket()

    def get_data(self, path_in_firebase):
        return db.reference(f'{path_in_firebase}').get()
    
    def add_data(self, path_in_firebase, data):
        db.reference(f'{path_in_firebase}').update(data)

    def get_photo(self, name):
        try:
            self.blob = self.bucket.blob(f'Avs/{name}.jpeg')
            self.blob.download_to_filename(f'{name}.jpeg')
            return True
        except Exception:
            return False

    def add_photo(self, name, data):
        try:   
            self.blob = self.bucket.blob(f'Avs/{name}.jpeg')
            self.blob.upload_from_filename(f'{name}.jpeg')
            return True
        except Exception:
            return False