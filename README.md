# 🌊 FloodVision — Global Solution FIAP | 2026 1° Semestre

<div align="center">

## 🛰️ Transformando dados espaciais em soluções na Terra!

Sistema preditivo de enchentes urbanas utilizando **Data Science**, **Inteligência Artificial** e **dados espaciais** para gerar alertas preventivos e apoiar decisões estratégicas em tempo real.

---

# 📌 Sobre o Projeto

O FloodVision é uma solução desenvolvida para a Global Solution 1° Semestre 2026 da FIAP com o objetivo de prever riscos de enchentes urbanas utilizando dados meteorológicos, análise de dados e Machine Learning.

A plataforma coleta informações climáticas em tempo real, processa os dados e estima o nível de risco de enchentes em regiões monitoradas, permitindo a geração de alertas preventivos e apoiando a tomada de decisões.

</div>

---

## 🚨 Problema

Todos os anos, enchentes causam prejuízos financeiros, danos à infraestrutura e colocam vidas em risco.

Muitas dessas ocorrências poderiam ser mitigadas através da utilização de sistemas preditivos capazes de identificar padrões climáticos e emitir alertas antecipados.

---

## 💡 Solução

A plataforma FloodVision utiliza dados meteorológicos para:

* Monitorar condições climáticas;
* Analisar padrões históricos;
* Identificar cenários de risco;
* Estimar a probabilidade de enchentes;
* Exibir resultados em uma interface interativa.

---

## 🏗️ Arquitetura do Projeto

```text
Coleta de Dados (Open-Meteo API)
            ↓
      Tratamento
            ↓
  Análise Exploratória
            ↓
 Machine Learning
            ↓
   Geração de Previsões
            ↓
 Dashboard Streamlit
```

---

## 📊 Dados Utilizados

As informações são coletadas através da API Open-Meteo.

### Variáveis utilizadas:

* Temperatura
* Umidade
* Precipitação
* Velocidade do vento
* Data e horário

### Cidades monitoradas:

* São Paulo
* Guarulhos
* Santo André

---

## 🤖 Machine Learning (Random Forest)

O modelo é treinado para identificar padrões associados a situações de risco.

### Etapas do processo:

* Coleta dos dados
* Tratamento dos dados
* Engenharia de atributos
* Treinamento do modelo
* Avaliação dos resultados
* Predição de riscos

---

## 🖥️ Dashboard

O sistema possui uma interface desenvolvida com Streamlit para visualização dos dados e previsões.

### Funcionalidades:

* Visualização dos indicadores climáticos
* Consulta das cidades monitoradas
* Exibição do risco previsto
* Gráficos interativos
* Monitoramento simplificado para apoio à tomada de decisão

---

## 🛠️ Tecnologias Utilizadas

* Python
* Pandas
* NumPy
* Scikit-Learn
* Streamlit
* Open-Meteo API
* Git
* GitHub

---

## 📂 Estrutura do Projeto

```text
FloodVision_GS/
│
├── data/
│   ├── bruto/
│   └── tratado/
│
├── notebooks/
│
├── src/
│   ├── coleta.py
│   ├── tratamento.py
│   ├── treinamento.py
│
├── streamlit_app.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🚀 Como Executar

```bash
git clone <repositorio>

cd FloodVision_GS

pip install -r requirements.txt

streamlit run streamlit_app.py
```

---

## 👨‍💻 Equipe

### Daniel Bissiato
- Coleta de dados
- Tratamento de dados
- Machine Learning

### Vinícius Barreto
- Visualização de dados
- Dashboard Streamlit

### Miguel Calabrez
- Pitch
- Documentação
- Apresentação

---

## 🎯 Objetivo

Transformar dados climáticos em informações estratégicas para auxiliar na prevenção de enchentes, contribuindo para uma resposta mais rápida a eventos extremos e reduzindo impactos sociais, econômicos e ambientais causados por desastres naturais.

---

## 🤝 Contribuição

Sinta-se à vontade para contribuir com melhorias, sugestões ou novas funcionalidades.

---

## 📬 Contato

Caso queira trocar ideias sobre o projeto ou compartilhar feedback, sinta-se à vontade para nos encontrar no LinkedIn:

* [Daniel Bissiato](https://www.linkedin.com/in/daniel-bissiato-b13a14344/)

* [Vinícius Barreto](https://www.linkedin.com/in/vin%C3%ADciusbarreto/)

* [Miguel Calabrez](https://www.linkedin.com/in/miguel-calabrez/)
