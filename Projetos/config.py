# config.py
# Centraliza a configuração do projeto.
# Regra de ouro: nenhuma chave de API fica escrita no código.

import os  # módulo padrão do Python para ler variáveis de ambiente
from dotenv import load_dotenv  # função que lê o arquivo .env

load_dotenv() # carrega as variáveis do .env para o ambiente

# Chaves lidas do ambiente (nunca escritas aqui):
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")# chave do Claude (Anthropic)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")# chave do GPT (OpenAI)

# IDs dos modelos, reunidos em um só lugar para trocar com facilidade.
# ATENÇÃO: nomes de modelo mudam com o tempo. Confirme o ID atual em:
#Anthropic -> https://docs.claude.com/en/docs/about-claude/models
#OpenAI-> https://platform.openai.com/docs/models
MODELO_ANTHROPIC = "claude-sonnet-5"# modelo da Anthropic
MODELO_OPENAI = "gpt-5.4"# modelo da OpenAI