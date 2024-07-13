import requests
from .auth import authenticate
import json

def send_to_model(auth_url, api_key, url, processed_text, template_request_text):
    if not authenticate(auth_url, api_key):
        return "Invalid API Key"

    # Reemplazar {{url}}, {{api_key}} y {{prompt}} en la plantilla de solicitud
    template_request_text = template_request_text.replace('{{url}}', url).replace('{{api_key}}', api_key).replace('{{prompt}}', processed_text)

    # Convertir el texto JSON en un diccionario de Python
    template_dict = json.loads(template_request_text)

    # Extraer datos del diccionario
    request_url = template_dict.get('url', '')
    payload = template_dict.get('payload', {})
    headers = template_dict.get('headers', {})

    # Añadir el encabezado de autorización
    headers['Authorization'] = f'Bearer {api_key}'
    print(request_url)
    print(payload)
    print(headers)
    print(template_request_text)
    print(processed_text)

    try:
        response = requests.post(request_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get('textResponse')
    except requests.exceptions.HTTPError as http_err:
        return f'HTTP error occurred: {http_err}\nResponse content: {response.content}'
    except Exception as err:
        print(err)
        return f'Other error occurred: {err}'

"""
   {
    "ur": "{url}}/chat",
    "payload": {
        "message": "{{prompt}}",
        "mode": "chat"
    },
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer {{api_key}}"
    }
} 
"""

#https://localhost:3001/api/v1/workspace/your_workspace_name_with_dashes_instead_of_spaces/chat 
#https://localhost:3001/api/v1/workspace/Long_Pdf_Test/chat

# http://localhost:3001/api/v1/workspace/Test
# http://localhost:3001/api/v1/auth
# KH2KRJ8-GAA4VQR-K6CR5QZ-JHM75PR
# http://localhost:3001/api/v1/workspace/Test
# http://localhost:3001/api/v1/auth
# KH2KRJ8-GAA4VQR-K6CR5QZ-JHM75PR