# enriquecer.py
# Pipeline do Encontro 2: le uma lista de empresas (CNPJs), consulta cada
# uma na BrasilAPI, pede ao LLM para classificar e grava um CSV enriquecido.
# Uma linha reta: ler, consultar, classificar, gravar.

import csv# ler e escrever CSV (vem com o Python)
import json# transformar o texto JSON do LLM em dicionario
import re  # limpar o CNPJ (deixar so os digitos)
import time # pausar entre as consultas (respeito a API)
import requests # fazer requisicoes HTTP (a API)
from providers import chat # reaproveitamos a funcao do Encontro 1

# Endereco da BrasilAPI para consulta de CNPJ (publica e gratuita).
URL_BRASILAPI = "https://brasilapi.com.br/api/cnpj/v1/"

def buscar_empresa(cnpj):
    """Consulta um CNPJ na BrasilAPI. Devolve um dicionario ou None."""
    so_digitos = re.sub(r"\D", "", cnpj)      # deixa so os numeros

    try:
        resposta = requests.get(URL_BRASILAPI + so_digitos, timeout=20)
    except requests.RequestException as erro:  # rede caiu, timeout, etc.
        print(f"  [aviso] falha de rede no CNPJ {so_digitos}: {erro}")
        return None                            # pula esta e segue as outras

    if resposta.status_code != 200:            # 200 = ok; senao, sem dados
        print(f"  [aviso] CNPJ {so_digitos} sem dados (HTTP {resposta.status_code})")
        return None

    dados = resposta.json()                    # a resposta JSON vira dicionario

    # .get() evita quebrar se algum campo vier ausente:
    return {
        "cnpj": so_digitos,
        "razao_social": dados.get("razao_social", ""),
        "nome_fantasia": dados.get("nome_fantasia", ""),
        "atividade": dados.get("cnae_fiscal_descricao", ""),
        "porte": dados.get("porte", ""),
        "municipio": dados.get("municipio", ""),
        "uf": dados.get("uf", ""),
        "capital_social": dados.get("capital_social", ""),
    }

# Instrucao de comportamento para o LLM (vai no parametro "sistema" do chat()).

SISTEMA_CLASSIFICADOR = (
    "Você é um analista de qualificação de leads B2B para o FlowDesk, um SaaS de CRM. "
    "A partir dos dados de uma empresa, responda APENAS com um JSON (sem texto antes "
    "ou depois) com as chaves: segmento (o setor de mercado em poucas palavras), "
    "porte (pequeno, médio ou grande), resumo (uma frase sobre a empresa) e "
    "nota_fit (um número de 0 a 10 indicando quão promissor é como lead) e "
    "explicabilidade (uma frase curta justificando a nota que você deu)."
)

def classificar_empresa(empresa):
    """Manda a empresa ao LLM e devolve segmento, porte, resumo, nota_fit
    e explicabilidade (a justificativa da nota)."""
    conteudo = (                              # monta o texto com os dados
        f"Razão social: {empresa['razao_social']}\n"
        f"Nome fantasia: {empresa['nome_fantasia']}\n"
        f"Atividade principal: {empresa['atividade']}\n"
        f"Porte (Receita): {empresa['porte']}\n"
        f"Cidade/UF: {empresa['municipio']}/{empresa['uf']}\n"
        f"Capital social: {empresa['capital_social']}"
    )
    mensagens = [{"role": "user", "content": conteudo}]

    # Reaproveita o chat() do Encontro 1. Trocar por "openai" tambem funciona.
    resposta = chat("anthropic", mensagens, sistema=SISTEMA_CLASSIFICADOR)

    # O modelo as vezes poe texto em volta do JSON. Pegamos do 1o { ao ultimo }:
    inicio = resposta.find("{")
    fim = resposta.rfind("}")
    texto = resposta[inicio:fim + 1] if inicio != -1 and fim != -1 else resposta

    try:
        dados = json.loads(texto)             # texto JSON vira dicionario
        return {
            "segmento": dados.get("segmento", ""),
            "porte_avaliado": dados.get("porte", ""),
            "resumo": dados.get("resumo", ""),
            "nota_fit": dados.get("nota_fit", ""),
            "explicabilidade": dados.get("explicabilidade", ""),
        }
    except json.JSONDecodeError:              # nao veio JSON valido: nao paramos
        print("  [aviso] o LLM nao devolveu JSON valido; campos vazios")
        # ATENCAO: as chaves aqui precisam ser AS MESMAS do return acima.
        # Se faltar ou sobrar uma, o DictWriter quebra na hora de gravar.
        return {"segmento": "", "porte_avaliado": "", "resumo": "",
                "nota_fit": "", "explicabilidade": ""}
    

def main():
    linhas_saida = []                         # acumula os resultados

    # 1) LER: percorremos cada CNPJ do CSV de entrada.
    # utf-8-sig tolera arquivo salvo pelo Excel (que tem um BOM invisivel).
    with open("empresas.csv", newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)      # cada linha vira um dicionario
        for linha in leitor:
            cnpj = linha["cnpj"]
            print(f"Processando {cnpj}...")

            empresa = buscar_empresa(cnpj)    # 2) CONSULTAR na BrasilAPI
            if empresa is None:               # nao achou/falhou: pula
                continue

            analise = classificar_empresa(empresa)   # 3) CLASSIFICAR no LLM

            linha_final = empresa.copy()      # comeca com os dados da empresa
            linha_final.update(analise)       # acrescenta a analise do LLM
            linhas_saida.append(linha_final)

            time.sleep(3)                     # pausa de 3s (com a API)

    # 4) GRAVAR: escrevemos tudo num CSV de saida.
    if not linhas_saida:
        print("Nenhuma empresa processada. Verifique o empresas.csv.")
        return

    colunas = list(linhas_saida[0].keys())    # nomes das colunas
    # utf-8-sig faz o Excel exibir os acentos (São, ção) corretamente.
    with open("empresas_enriquecidas.csv", "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()                # linha de cabecalho
        escritor.writerows(linhas_saida)      # todas as linhas

    print(f"Pronto! {len(linhas_saida)} empresas em empresas_enriquecidas.csv")


# Faz o main() rodar quando executamos "python enriquecer.py".
if __name__ == "__main__":
    main()
