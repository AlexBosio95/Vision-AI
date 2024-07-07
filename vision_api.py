import warnings

# Ignora gli avvisi specifici di urllib3
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")

import base64
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Percorso del file delle chiavi di servizio (nella stessa cartella dello script)
KEY_PATH = 'service-account-file.json'  # Cambia con il nome effettivo del file

# URL dell'API di Google Vision AI
VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate'

# Carica le credenziali di servizio
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
auth_req = Request()
scoped_credentials.refresh(auth_req)

# Funzione per convertire l'immagine in base64
def image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Funzione per chiamare le API di Google Vision
def call_google_vision_api(image_path):
    image_base64 = image_to_base64(image_path)

    # Corpo della richiesta
    request_body = {
        'requests': [
            {
                'image': {
                    'content': image_base64
                },
                'features': [
                    {
                        'type': 'LABEL_DETECTION',
                        'maxResults': 10
                    }
                ]
            }
        ]
    }

    headers = {
        'Authorization': f'Bearer {scoped_credentials.token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(VISION_API_URL, headers=headers, json=request_body)
    return response.json()

# Funzione per generare il contenuto HTML
def generate_html(response_json, image_path, encoded_image):
    labels = []
    scores = []

    for annotation in response_json['responses'][0]['labelAnnotations']:
        labels.append(annotation['description'])
        scores.append(round(annotation['score'] * 100, 2))

    labels_html = "".join(
        f'<div class="label"><span>{label}</span><div class="progress"><div class="progress-bar" style="width: {score}%;" data-label="{score}%"></div></div></div>'
        for label, score in zip(labels, scores)
    )

    with open('template.html', 'r') as file:
        html_template = file.read()

    html_content = html_template.replace('{{encoded_image}}', encoded_image).replace('{{labels}}', labels_html)

    return html_content

# Chiede all'utente di specificare il percorso dell'immagine
image_path = input("Inserisci il percorso dell'immagine: ")

# Codifica l'immagine in base64 per l'inclusione nell'HTML
encoded_image = image_to_base64(image_path)

# Chiamata alla funzione e generazione dell'HTML
response_json = call_google_vision_api(image_path)
html_content = generate_html(response_json, image_path, encoded_image)

# Salva il risultato in un file HTML
with open('vision_results.html', 'w') as outfile:
    outfile.write(html_content)

print("Risultati salvati in 'vision_results.html'")
