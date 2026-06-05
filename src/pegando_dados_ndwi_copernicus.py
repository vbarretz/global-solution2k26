import requests
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# credenciais
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')


def get_token():
    url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    response = requests.post(url, data={
        "client_id": "cdse-public",
        "grant_type": "password",
        "username": username,
        "password": password
    })
    return response.json()["access_token"]


# BUSCA IMAGENS SENTINEL-2 
def buscar_imagens(token, latitude, longitude, dias=30):
    
    # Define período de busca
    data_fim = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    data_inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Cria bounding box ao redor do ponto (0.1 grau ~ 11km)
    bbox = f"{longitude-0.1},{latitude-0.1},{longitude+0.1},{latitude+0.1}"
    
    url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
    
    params = {
        "$filter": f"Collection/Name eq 'SENTINEL-2' and OData.CSC.Intersects(area=geography'SRID=4326;POLYGON(({longitude-0.1} {latitude-0.1},{longitude+0.1} {latitude-0.1},{longitude+0.1} {latitude+0.1},{longitude-0.1} {latitude+0.1},{longitude-0.1} {latitude-0.1}))') and ContentDate/Start gt {data_inicio} and ContentDate/Start lt {data_fim} and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 30.0)",
        "$orderby": "ContentDate/Start desc",
        "$top": 3
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, params=params, headers=headers)
    
    return response.json()


# ndwi aproximado
def calcular_ndwi_aproximado(token, latitude, longitude):
   
    
    bbox = f"{longitude-0.05},{latitude-0.05},{longitude+0.05},{latitude+0.05}"
    data_fim = datetime.now().strftime("%Y-%m-%d")
    data_inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    url = "https://sh.dataspace.copernicus.eu/api/v1/statistics"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {
            "bounds": {
                "bbox": [longitude-0.05, latitude-0.05, longitude+0.05, latitude+0.05],
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
            },
            "data": [{
                "dataFilter": {
                    "timeRange": {
                        "from": f"{data_inicio}T00:00:00Z",
                        "to": f"{data_fim}T23:59:59Z"
                    },
                    "maxCloudCoverage": 30
                },
                "type": "sentinel-2-l2a"
            }]
        },
        "aggregation": {
            "timeRange": {
                "from": f"{data_inicio}T00:00:00Z",
                "to": f"{data_fim}T23:59:59Z"
            },
            "aggregationInterval": {"of": "P30D"},
            "evalscript": """
                //VERSION=3
                function setup() {
                    return {
                        input: [{bands: ["B03", "B08", "dataMask"]}],
                        output: [
                            {id: "ndwi", bands: 1, sampleType: "FLOAT32"},
                            {id: "dataMask", bands: 1, sampleType: "UINT8"}
                        ]
                    };
                }
                function evaluatePixel(sample) {
                    let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
                    return {
                        ndwi: [ndwi],
                        dataMask: [sample.dataMask]
                    };
                }
            """
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response

# coleta ndwi
print(" CONECTANDO AO SENTINEL-2...")
token = get_token()
print(" Token obtido!")

cidades = {
    'Sao_Paulo':  {'lat': -23.55, 'lon': -46.63},
    'Guarulhos':  {'lat': -23.46, 'lon': -46.53},
    'Santo_Andre': {'lat': -23.65, 'lon': -46.53}
}

resultados = []

for cidade, coords in cidades.items():
    print(f"\nBuscando NDWI para {cidade}...")
    
    response = calcular_ndwi_aproximado(token, coords['lat'], coords['lon'])
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Resposta: {data}")
        
        # Tenta extrair o valor NDWI
        try:
            ndwi_valor = data['data'][0]['outputs']['ndwi']['bands']['B0']['stats']['mean']
            print(f"NDWI {cidade}: {ndwi_valor:.4f}")
        except:
            ndwi_valor = None
            print(f" Não conseguiu extrair NDWI de {cidade}")
    else:
        print(f"Erro: {response.text[:200]}")
        ndwi_valor = None
    
    resultados.append({
        'cidade': cidade,
        'latitude': coords['lat'],
        'longitude': coords['lon'],
        'ndwi': ndwi_valor,
        'data_coleta': datetime.now().strftime("%Y-%m-%d")
    })

# Salvando resultado
df_ndwi = pd.DataFrame(resultados)
print("\n=== RESULTADO NDWI ===")
print(df_ndwi)

df_ndwi.to_csv('dados_ndwi.csv', index=False)
print("\n Salvo")
