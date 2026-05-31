import json
import requests


url = "https://api.open-meteo.com/v1/forecast?latitude=-23.55&longitude=-46.63&hourly=precipitation&timezone=America/Sao_Paulo&past_days=7"


response = requests.get(url)


data = response.json()

with open('dados_api.json', 'w', encoding='utf-8') as arquivo:
    json.dump(data, arquivo, ensure_ascii=False, indent=4)
