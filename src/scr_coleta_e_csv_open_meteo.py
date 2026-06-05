import pandas as pd
import requests


# cidades que vamos coletar os dados
cidades = {
    'Sao_Paulo': {'lat': -23.55, 'lon': -46.63},
    'Guarulhos': {'lat': -23.46, 'lon': -46.53},
    'Santo_Andre': {'lat': -23.65, 'lon': -46.53}
}


# url base
url_base = 'https://api.open-meteo.com/v1/forecast'


# parâmetros
parametros = {
    'hourly': 'temperature_2m,relative_humidity_2m,precipitation',
    'timezone': 'America/Sao_Paulo',
    'past_days': 31 # alteravel dps
}


#armazenar as cidades
dados = {}


# coleta para cada cidade
for cidade, coords in cidades.items():
    print(f'\ncoletando dados de {cidade}...\n')

# colocando coordenadas para os parâmetros
    params = parametros.copy()

    params['latitude'] = coords['lat']

    params['longitude'] = coords['lon']

# fazendo a requisião
    response = requests.get(url_base, params=params)
    data = response.json()

# extraindo os dados
    times = data['hourly']['time']

    temp = data['hourly']['temperature_2m']

    umidade = data['hourly']['relative_humidity_2m']

    precipitacao = data['hourly']['precipitation']

# criando o df
    df = pd.DataFrame({
        'data_hora': times,
        'temperatura': temp,
        'umidade': umidade,
        'precipitacao': precipitacao,
        'cidade': cidade
    })

    dados[cidade] = df
    print(f'\n* {cidade}: {len(df)} registros coletados')


# tudo isso em um só df
df_df = pd.concat(dados.values(), ignore_index=True)

# salvando em csv
df_df.to_csv('dados_clima_bruto.csv', index= False)
print(f'\n* Total de {len(df_df)} registros salvos em \033[32mdados_clima_bruto.csv\033[m\n')
print(df_df.head())
