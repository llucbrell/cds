import requests

def send_to_model(burl, text):
    url = f"{burl}/chat"
    payload = {
        "message": text,
        "mode": "chat"
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY'  # Asegúrate de que este encabezado es correcto
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get('textResponse')
    except requests.exceptions.RequestException as e:
        return str(e)

#https://localhost:3001/api/v1/workspace/your_workspace_name_with_dashes_instead_of_spaces/chat 
#https://localhost:3001/api/v1/workspace/Long_Pdf_Test/chat
