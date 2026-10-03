# Qualificador de Leads B2B

Ferramenta de qualificação de leads B2B construída em Python puro, do zero.
Ela consulta os dados públicos de uma empresa pelo CNPJ (BrasilAPI) e usa um
LLM (Claude / GPT) para classificar cada empresa: segmento, porte, um resumo
e uma nota de "fit" como potencial cliente.

Projeto construído em três encontros no pela pós de engenharia de dados.

## O que ele faz

- **Camada de provider** (`providers.py`): uma função `chat()` que fala com
  Anthropic e OpenAI trocando apenas uma variável.
- **Pipeline** (`enriquecer.py`): lê um CSV de empresas, consulta a BrasilAPI
  e gera um CSV enriquecido com a análise do LLM.
- **Agente** (`agente.py`): o LLM decide sozinho quando consultar a empresa,
  usando a busca como uma ferramenta (tool use).

## Estrutura

    qualificador-leads-b2b/
    ├── config.py         # chaves e modelos (lê do .env)
    ├── providers.py      # a função chat() (Anthropic + OpenAI)
    ├── enriquecer.py     # o pipeline: CSV -> BrasilAPI -> LLM -> CSV
    ├── agente.py         # o agente com tool use
    ├── empresas.csv      # lista de CNPJs de entrada
    ├── requirements.txt
    ├── conftest.py
    └── tests/            # testes automatizados

