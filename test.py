import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("api_keys/simplechat-39233-firebase-adminsdk-1e0ku-2bcaa707e7.json")

default_app = firebase_admin.initialize_app(cred, {
	  'databaseURL': 'https://simplechat-39233-default-rtdb.europe-west1.firebasedatabase.app/',
    'storageBucket' : 'storage-bucket-local-name'
	})

bucket = storage.bucket()


messages = {
	"12": {
        "2": {
            "messages": {
                "12": "Привет, как дела?",
                "2": "Привет"
            }
        }
    }
}

db.reference("/Messages/").set(messages)

print(db.reference("/").get())


