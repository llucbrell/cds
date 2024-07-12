import requests

def authenticate(auth_url, api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(auth_url, headers=headers)
        response.raise_for_status()
        auth_response = response.json()
        if auth_response.get("authenticated"):
            return True
        return False
    except requests.exceptions.RequestException as e:
        return str(e)
