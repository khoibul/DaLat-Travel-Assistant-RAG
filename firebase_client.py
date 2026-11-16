import os
import requests
from dotenv import load_dotenv

load_dotenv()

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
BASE_URL = "https://identitytoolkit.googleapis.com/v1/accounts"


def _auth_request(endpoint, email, password):
    if not FIREBASE_API_KEY:
        raise ValueError("FIREBASE_API_KEY is missing. Check your .env file.")

    url = f"{BASE_URL}:{endpoint}?key={FIREBASE_API_KEY}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        response = requests.post(url, json=payload, timeout=20)
        data = response.json()

        if not response.ok:
            error_code = data.get("error", {}).get("message", "UNKNOWN_ERROR")

            error_messages = {
                "EMAIL_EXISTS": "This email is already registered.",
                "INVALID_EMAIL": "The email address is invalid.",
                "WEAK_PASSWORD": "Password should be at least 6 characters.",
                "INVALID_PASSWORD": "Incorrect email or password.",
                "EMAIL_NOT_FOUND": "No account found with this email.",
                "USER_DISABLED": "This account has been disabled.",
                "OPERATION_NOT_ALLOWED": "Email/Password sign-in is not enabled.",
                "API_KEY_INVALID": "Firebase API key is invalid."
            }

            raise ValueError(error_messages.get(error_code, error_code))

        return data

    except requests.exceptions.Timeout:
        raise ConnectionError("Firebase request timed out.")

    except requests.exceptions.ConnectionError:
        raise ConnectionError("Could not connect to Firebase.")


def sign_up(email, password):
    """Create a new Firebase account."""
    return _auth_request("signUp", email, password)


def sign_in(email, password):
    """Sign in to an existing Firebase account."""
    return _auth_request("signInWithPassword", email, password)