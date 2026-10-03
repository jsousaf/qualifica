# providers.py
# A "camada de provider": uma única função chat() que fala com a
# Anthropic OU com a OpenAI, escondendo as diferenças entre as duas.

from anthropic import Anthropic
from openai import OpenAI  

from config import (
ANTHROPIC_API_KEY,
OPENAI_API_KEY,
MODELO_ANTHROPIC,
MODELO_OPENAI,
)

# Um "cliente" por provider: o objeto que efetua as chamadas.
# Eles são criados só na primeira vez em que o provider é usado ("preguiçosamente"),
# e não no import. Assim quem usa só o Claude não precisa da chave da OpenAI.

_clientes = {}  # guarda o cliente já criado, para não recriar a cada chamada

def _exigir_chave(chave, nome):
    """Interrompe com uma mensagem clara se a chave não estiver no .env."""
    if not chave:
        raise RuntimeError(
            f"{nome} não encontrada. Crie um arquivo .env na pasta do projeto "
            f"com a linha:  {nome}=sua-chave-aqui"
        )
    return chave

def _cliente(provider):
    """Devolve o cliente do provider, construindo-o na primeira chamada."""
    if provider not in _clientes:
        if provider == "anthropic":
            _clientes[provider] = Anthropic(
                api_key=_exigir_chave(ANTHROPIC_API_KEY, "ANTHROPIC_API_KEY")
            )
        else:
            _clientes[provider] = OpenAI(
                api_key=_exigir_chave(OPENAI_API_KEY, "OPENAI_API_KEY")
            )
    return _clientes[provider]


def chat(provider, mensagens, sistema="Você é um assistente prestativo sobre tecnologia."):
    """
    Envia uma conversa ao LLM e devolve o texto da resposta.

    provider : "anthropic" ou "openai"
    mensagens: lista como [{"role": "user", "content": "..."}]
    sistema  : instrução de comportamento (o "system"), com valor padrão.
    """
    if provider == "anthropic":                 # caminho do Claude
        resposta = _cliente("anthropic").messages.create(
            model=MODELO_ANTHROPIC,             # qual modelo usar
            max_tokens=4096,                    # teto da resposta (raciocínio + texto)
            system=sistema,                     # Anthropic: system é parâmetro separado
            messages=mensagens,                 # a conversa
        )
        # A resposta vem como uma LISTA de blocos, e nem todo bloco é texto:
        # nos modelos atuais o 1o pode ser um bloco de raciocínio ("thinking").
        # Por isso procuramos o primeiro bloco cujo tipo é "text".
        for bloco in resposta.content:
            if bloco.type == "text":
                return bloco.text
        raise RuntimeError(
            f"A Anthropic não devolveu texto (stop_reason={resposta.stop_reason}). "
            "Se for 'max_tokens', aumente o max_tokens."
        )

    elif provider == "openai":                  # caminho do GPT
        # OpenAI: o system entra como a primeira mensagem da lista.
        mensagens_openai = [{"role": "system", "content": sistema}] + mensagens
        resposta = _cliente("openai").chat.completions.create(
            model=MODELO_OPENAI,                # qual modelo usar
            messages=mensagens_openai,          # system + a conversa
        )
        return resposta.choices[0].message.content   # pega a mensagem da 1a escolha

    else:                                       # provider inválido
        raise ValueError(f"Provider desconhecido: {provider}")