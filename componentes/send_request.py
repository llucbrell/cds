import requests
from .auth import authenticate

def send_to_model(auth_url, api_key, burl, text):
    if not authenticate(auth_url, api_key):
        return "Invalid API Key"

    url = f"{burl}/chat"
    payload = {
        "message": text,
        "mode": "chat"
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get('textResponse')
    except requests.exceptions.HTTPError as http_err:
        return f'HTTP error occurred: {http_err}\nResponse content: {response.content}'
    except Exception as err:
        return f'Other error occurred: {err}'

#https://localhost:3001/api/v1/workspace/your_workspace_name_with_dashes_instead_of_spaces/chat 
#https://localhost:3001/api/v1/workspace/Long_Pdf_Test/chat

# http://localhost:3001/api/v1/workspace/Test
# http://localhost:3001/api/v1/auth
# KH2KRJ8-GAA4VQR-K6CR5QZ-JHM75PR
