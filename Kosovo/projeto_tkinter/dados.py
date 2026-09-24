from datetime import datetime
import json
import os

DIR_DADOS = "dados"
CAMINHO_JSON = os.path.join(DIR_DADOS, "produtos.json")
DIR_EVIDENCIAS = "evidencias"


def garantir_diretorios():
    """Garante a existência das pastas dados e evidencias."""
    if not os.path.exists(DIR_DADOS):
        os.makedirs(DIR_DADOS)
    if not os.path.exists(DIR_EVIDENCIAS):
        os.makedirs(DIR_EVIDENCIAS)


def carregar_produtos():
    """Carrega os produtos salvos ou cria lista padrão se o arquivo não existir."""
    garantir_diretorios()

    if not os.path.exists(CAMINHO_JSON):
        produtos_iniciais = [
            {"id": 1, "nome": "Camiseta Básica", "preco": 49.90, "estoque": 10},
            {"id": 2, "nome": "Calça Jeans", "preco": 129.90, "estoque": 5},
            {"id": 3, "nome": "Jaqueta de Couro", "preco": 299.90, "estoque": 3},
        ]
        salvar_produtos(produtos_iniciais)
        return produtos_iniciais

    try:
        with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise IOError(
            f"Erro ao ler o arquivo de dados '{CAMINHO_JSON}': {str(e)}"
        )


def salvar_produtos(produtos):
    """Grava a lista de produtos no JSON."""
    garantir_diretorios()
    try:
        with open(CAMINHO_JSON, "w", encoding="utf-8") as f:
            json.dump(produtos, f, indent=4, ensure_ascii=False)
    except Exception as e:
        raise IOError(f"Erro ao salvar dados em '{CAMINHO_JSON}': {str(e)}")


def gerar_proximo_id(produtos):
    """Gera o próximo ID sequencial."""
    if not produtos:
        return 1
    return max(p["id"] for p in produtos) + 1


def registrar_evidencia(acao, detalhes):
    """Grava um registro de auditoria/evidência na pasta evidencias/."""
    garantir_diretorios()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = os.path.join(
        DIR_EVIDENCIAS, f"evidencia_{acao}_{timestamp}.txt"
    )

    try:
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(f"=== EVIDÊNCIA DE OPERAÇÃO: {acao.upper()} ===\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("----------------------------------------\n")
            f.write(detalhes)
            f.write("\n----------------------------------------\n")
    except Exception as e:
        print(f"Falha ao registrar evidência: {e}")