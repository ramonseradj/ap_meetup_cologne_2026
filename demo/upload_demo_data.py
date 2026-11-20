from cryptography.fernet import Fernet
import pandas_gbq, pandas
from google.oauth2 import service_account

PROJECT_ID = "analytics-cologne"
SECRET_KEY = b'5og3EDC0SFn0A7Gnz6HKXxZXEOcywv7QrV2BzTy74gE='
DEMO_FILE = "demo/versicherung_chatbot_traces_demo.csv"
DEMO_TABLE = "ap_meetup_cologne.ap_meetup_demo"
CREDENTIAL_PARTH = "service_account.json"

cipher = Fernet(SECRET_KEY)
def encrypt_if_present(val):
    if pandas.isna(val):
        return None  # Preserves missing values as NULL for BigQuery
    return cipher.encrypt(str(val).encode("utf-8")).decode("utf-8")

# Load CSV and encrypt
data = pandas.read_csv(DEMO_FILE)
data["encrypted_chat_body"] = data["chat_body"].apply(
    encrypt_if_present
)
data = data.drop(columns=["chat_body"])

# Upload to BigQuery
credentials = service_account.Credentials.from_service_account_file(CREDENTIAL_PARTH)
pandas_gbq.to_gbq(
    data, 
    project_id = PROJECT_ID, 
    credentials = credentials, 
    destination_table = DEMO_TABLE, 
    if_exists="replace"
)
