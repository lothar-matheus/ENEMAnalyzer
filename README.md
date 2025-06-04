# 
# 📊 ENEMAnalyzer - Analisador Standalone dos Microdados do ENEM 2023

Este projeto é uma aplicação standalone em Python desenvolvida para processar, analisar e visualizar os **microdados do ENEM 2023**, utilizando **Pandas** e **Plotly** para gerar insights sobre o desempenho dos estudantes em todo o Brasil.

---

## ✅ Funcionalidades

- 📂 Carregamento de microdados (.csv) do ENEM 2023  
- 🔄 Pré-processamento: mapeamento de variáveis, criação de colunas auxiliares e filtragem  
- 📊 Estatísticas gerais: média das notas, distribuição por sexo e região  
- 📍 Análises específicas:
  - Desempenho médio por **estado e região**
  - Desempenho médio por **nível socioeconômico**  
- 📈 Geração de gráficos interativos com **Plotly**

---

## ⚙️ Principais Funções

### `carregar_dados(amostra=None)`
- **O que faz:** Carrega os microdados do arquivo CSV.
- **Parâmetros:** `amostra` (int, opcional) - número de linhas para testes.
- **Uso:** `analise.carregar_dados(amostra=50000)`

### `processar_dados()`
- **O que faz:** Pré-processa os dados: filtra, mapeia e cria novas colunas.

### `estatisticas_gerais()`
- **O que faz:** Exibe estatísticas básicas (médias, totais, distribuição por sexo e região).

### `analise_1_desempenho_por_estado()`
- **O que faz:** Cria gráfico com a média das notas totais por estado.

### `analise_2_desempenho_por_nivel_socioeconomico()`
- **O que faz:** Cria gráfico com a média das notas por renda familiar (Q006).

### `analise_3_maiores_notas_redacao(self)`
- **O que faz:** Realiza a identificação das três maiores notas de redação entre os candidatos, apresentando os registros completos correspondentes a essas notas. Ideal para destacar os melhores desempenhos individuais nesta área.

### `analise_4_genero_areas(self)`
- **O que faz:** Gera uma análise comparativa entre o desempenho médio por área de conhecimento (Linguagens, Matemática, Ciências Humanas, Ciências da Natureza e Redação), segmentada por gênero. Auxilia na compreensão de eventuais disparidades de desempenho entre candidatos do sexo masculino e feminino.

---

## 🧠 Tecnologias Utilizadas

- Python 3.9+
- Pandas, NumPy
- Plotly
- Jupyter (opcional)

---

## 🗂️ Estrutura do Projeto

```
📁 ENEMAnalyzer/
├── enem_analyzer.py
├── MICRODADOS_ENEM_2023.csv
└── README.md
```

---

## 🚀 Como Executar

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/ENEMAnalyzer.git
cd ENEMAnalyzer
```

2. Instale as dependências:
```bash
pip install pandas numpy plotly
```

3. Baixe os microdados do ENEM 2023:
https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enem/microdados

4. Coloque o arquivo `MICRODADOS_ENEM_2023.csv` na pasta do projeto.

5. Execute o script principal:
```python
```


