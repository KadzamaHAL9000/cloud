import os

FIREBASE_STORAGE_USER_FOLDER: str = "user"
FIREBASE_STORAGE_STL_GENERATOR_FOLDER: str = "stl-generator"
FIREBASE_USER_DRAWING_FIRESTORE_COLLECTION: str = "user-drawing"
FIREBASE_USER_DRAWING_STORAGE_GCODE_FILENAME: str = "drawing.gcode"
FIREBASE_USER_DRAWING_STORAGE_TEXT2STL_FILENAME: str = "3DText.stl"

FIREBASE_CONFIG: dict = {
    "apiKey": os.getenv(
        "FIREBASE_CONFIG_API_KEY", "AIzaSyDsEXIV0OTzWuRX4XBiVB4a-3w4bP_fnCs"
    ),
    "authDomain": os.getenv(
        "FIREBASE_CONFIG_AUTH_DOMAIN", "chocolate-fiesta-cloud.firebaseapp.com"
    ),
    "projectId": os.getenv("FIREBASE_CONFIG_PROJECT_ID", "chocolate-fiesta-cloud"),
    "storageBucket": os.getenv(
        "FIREBASE_CONFIG_STORAGE_BUCKET", "chocolate-fiesta-cloud.appspot.com"
    ),
    "messagingSenderId": os.getenv(
        "FIREBASE_CONFIG_MESSAGING_SENDER_ID", "419100703725"
    ),
    "appId": os.getenv(
        "FIREBASE_CONFIG_APP_ID", "1:419100703725:web:42a642a456befea15045e4"
    ),
}

FIREBASE_CREDENTIALS = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID", "chocolate-fiesta-cloud"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
    "client_email": "chocolate-fiesta-cloud@appspot.gserviceaccount.com",
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv(
        "FIREBASE_CLIENT_X509_CERT_URL",
        "https://www.googleapis.com/robot/v1/metadata/x509/chocolate-fiesta-cloud%40appspot.gserviceaccount.com",
    ),
}


CORS_MIDDLEWARE_ALLOW_ORIGINS: list = os.getenv(
    "CORS_MIDDLEWARE_ALLOW_ORIGINS",
    "http://localhost:3000,https://cloud.chocolatefiesta.ru",
).split(",")

SENTRY_SDK_URL: str = os.getenv(
    "SENTRY_SDK_URL",
    "https://41408919c9984e58a69828c9ee33118b@o528559.ingest.sentry.io/5645977",
)

OPENSCAD_EXECUTABLE_PATH: str = os.getenv("OPENSCAD_EXECUTABLE", "openscad")
