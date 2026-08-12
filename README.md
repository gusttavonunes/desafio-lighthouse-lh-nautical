```
desafio_lh_nautical/
├── data/
│   ├── 01_bronze/         # Dados brutos (landing zone). Onde ficarão os 24 CSVs originais. Imutável.
│   ├── 02_silver/         # Dados limpos, tipados, padronizados, deduplicados e enriquecidos.
│   └── 03_gold/           # Tabelas de negócios (Data Marts), métricas para a Marina e features para IA.
├── notebooks/             # Exploração inicial (EDA), rascunhos de hipóteses e documentação visual.
├── src/                   # Código fonte principal do pipeline
│   ├── config/            # Configurações globais (esquemas, mapeamento de caminhos, parâmetros).
│   ├── ingestion/         # Scripts para leitura e validação da camada Bronze.
│   ├── processing/        # Transformações da Bronze para Silver (tratamento de dados).
│   ├── business/          # Regras de negócio da Silver para Gold (agregações, KPIs).
│   ├── modeling/          # Lógicas de Machine Learning (previsão de demanda, recomendação).
│   └── utils/             # Funções auxiliares (logs, tratamento de exceções).
├── docs/                  # Documentação técnica, dicionário de dados e arquitetura (foco no Gabriel).
├── dashboards/            # Arquivos de visualização (scripts, PBIX ou PDFs gerados).
├── tests/                 # Testes unitários e de qualidade de dados (garantia para o Sr. Almir).
├── requirements.txt       # Dependências do projeto (pandas, scikit-learn, etc.).
└── README.md              # Visão geral do projeto e instruções de execução.
