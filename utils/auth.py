import subprocess
from google.oauth2 import service_account

def get_access_token():
    """Get access token for API calls using gcloud CLI."""
    try:
        result = subprocess.run(
            ['gcloud', 'auth', 'print-access-token'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f'Failed to get access token: {e}')

def get_credentials(credentials_path):
    """Get credentials from service account key file."""
    return service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )