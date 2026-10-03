# agente.py
# transformamos buscar_empresa numa FERRAMENTA que o proprio
# LLM decide usar. Isso e "tool use", o coracao de um agente.
#
# O fluxo: descrevemos a ferramenta -> o modelo pede para usa-la ->
# nos executamos -> devolvemos o resultado -> o modelo responde.

import json                                  # para serializar o resultado da ferramenta

from anthropic import Anthropic              # SDK da Anthropic (usamos o Claude aqui)

from config import ANTHROPIC_API_KEY, MODELO_ANTHROPIC
from enriquecer import buscar_empresa   

# A DESCRICAO da ferramenta: e assim que o modelo fica sabendo que ela existe.
# Nome, o que faz, e quais parametros recebe.
FERRAMENTAS = [
    {
        "name": "buscar_empresa",
        "description": "Busca dados publicos de uma empresa brasileira pelo CNPJ.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cnpj": {"type": "string", "description": "O CNPJ da empresa"},
            },
            "required": ["cnpj"],
        },
    }
]

SISTEMA = (
    "Você é um assistente de qualificação de leads B2B. Quando o usuário pedir "
    "informações sobre uma empresa, use a ferramenta buscar_empresa para obter "
    "os dados e então responda com um resumo e uma nota de fit de 0 a 10."
)


def rodar_agente(pergunta):
    """Conversa com o modelo, deixando que ele use a ferramenta quando quiser."""
    cliente = Anthropic(api_key=ANTHROPIC_API_KEY)
    mensagens = [{"role": "user", "content": pergunta}]

    for _ in range(5):                        # limite de seguranca: no maximo 5 voltas
        resposta = cliente.messages.create(
            model=MODELO_ANTHROPIC,
            max_tokens=1024,
            system=SISTEMA,
            tools=FERRAMENTAS,                # entregamos a lista de ferramentas
            messages=mensagens,
        )

        # Guardamos a resposta do modelo na conversa.
        mensagens.append({"role": "assistant", "content": resposta.content})

        # Se o modelo NAO pediu ferramenta, a resposta final ja chegou.
        if resposta.stop_reason != "tool_use":
            texto_final = ""
            for bloco in resposta.content:    # juntamos os pedacos de texto
                if bloco.type == "text":
                    texto_final += bloco.text
            return texto_final

        # Se pediu, executamos cada ferramenta e preparamos os resultados.
        resultados = []
        for bloco in resposta.content:
            if bloco.type == "tool_use":      # este bloco e um pedido de ferramenta
                print(f"  [agente] chamando {bloco.name}({bloco.input})")

                if bloco.name == "buscar_empresa":     # so temos esta ferramenta
                    dados = buscar_empresa(bloco.input["cnpj"])
                else:
                    dados = None

                resultados.append({                    # formato que o modelo espera
                    "type": "tool_result",
                    "tool_use_id": bloco.id,
                    "content": json.dumps(dados, ensure_ascii=False),
                })

        # Devolvemos os resultados ao modelo como uma nova mensagem.
        mensagens.append({"role": "user", "content": resultados})

    return "O agente atingiu o limite de voltas sem concluir."

if __name__ == "__main__":
    pergunta = "O que é um LLM?"
    print(rodar_agente(pergunta))