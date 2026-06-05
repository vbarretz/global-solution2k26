import requests
import os
from dotenv import load_dotenv

load_dotenv()

# credenciais da copernicus
username = os.getenv('USERNAME')
passoword = os.getenv('PASSWORD')


# url do token
url_token = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'


#pegar os dados
response = requests.post(url_token, data={
    'client_id': 'cdse-public',
    'grant_type': 'password',
    'username': username,
    'password': passoword
})


# verificação de erro
if response.status_code == 200:
    token = response.json()['access_token']
    print('loggin realizado')
    print(f'token: {token[:50]}')
else:
    print(f'erro: {response.status_code}')
    print(response.json())
