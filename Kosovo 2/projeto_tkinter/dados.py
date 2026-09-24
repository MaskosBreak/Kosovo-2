import json
import os

CAMINHO_JSON = os.path.join("dados", "produtos.json")


def carregar_produtos():
    """Carrega os produtos do arquivo JSON ou cria o arquivo padrão caso não exista."""
    if not os.path.exists("dados"):
        os.makedirs("dados")

    if not os.path.exists(CAMINHO_JSON):
        produtos_iniciais = [
            {"id": 1, "nome": "Camiseta Básica", "preco": 49.90, "estoque": 10},
            {"id": 2, "nome": "Calça Jeans", "preco": 129.90, "estoque": 5},
        ]
        salvar_produtos(produtos_iniciais)
        return produtos_iniciais

    with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_produtos(produtos):
    """Salva a lista de produtos atualizada no JSON."""
    if not os.path.exists("dados"):
        os.makedirs("dados")

    with open(CAMINHO_JSON, "w", encoding="utf-8") as f:
        json.dump(produtos, f, indent=4, ensure_ascii=False)