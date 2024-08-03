import requests
from .auth import authenticate
import json

def get_response_content(response_json):
    print("Response format")
    print(response_json)
    if 'choices' in response_json:
        # LM studio
        # Asumiendo que 'choices' es una lista de objetos y queremos extraer 'content' del objeto 'message'
        #choices = [choice['message']['content'] for choice in response_json['choices']]
        return response_json['choices'][0]['message']['content']
    elif 'textResponse' in response_json:
        # Anything LM
        return response_json['textResponse']
    elif 'response' in response_json:  # Ejemplo de un nuevo tipo de respuesta
        return response_json['response']
    else:
        return 'Unknown response format ' + response_json


def send_request(request_url, payload, headers):
    try:
        response = requests.post(request_url, json=payload, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        return get_response_content(response_json)
    except requests.exceptions.HTTPError as http_err:
        return f'HTTP error occurred: {http_err}\nResponse content: {response.content}'
    except Exception as err:
        print(err)
        return f'Other error occurred: {err}'


def send_to_model(auth_url, api_key, url, model_name ,processed_text, template_request_text):
    if not authenticate(auth_url, api_key):
        return "Invalid API Key"
     
    # Usar json.dumps para escaparse el processed_text
    processed_text_escaped = json.dumps(processed_text)[1:-1]

    # Reemplazar {{url}}, {{api_key}} y {{prompt}} en la plantilla de solicitud
    template_request_text = template_request_text.replace('{{url}}', url).replace('{{api_key}}', api_key).replace('{{prompt}}', processed_text_escaped).replace('{{model_name}}', model_name)


    print(template_request_text)
    # Convertir el texto JSON en un diccionario de Python
    template_dict = json.loads(template_request_text)

    # Extraer datos del diccionario
    request_url = template_dict.get('url', '')
    payload = template_dict.get('payload', {})
    headers = template_dict.get('headers', {})

    # Añadir el encabezado de autorización
    headers['Authorization'] = f'Bearer {api_key}'

    try:
        response = requests.post(request_url, json=payload, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        return get_response_content(response_json)
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