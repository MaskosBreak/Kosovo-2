def validar_produto_formulario(nome, preco_str, estoque_str):
    """
    Valida e converte os campos do formulário de produto.
    Retorna (sucesso, dict_dados_ou_mensagem_erro)
    """
    nome_limpo = nome.strip()
    if not nome_limpo:
        return False, "O campo 'Nome do Produto' é obrigatório."

    if len(nome_limpo) < 2 or len(nome_limpo) > 50:
        return False, "O nome do produto deve ter entre 2 e 50 caracteres."

    # Validação do Preço
    try:
        preco_formatado = preco_str.replace(",", ".").strip()
        preco = float(preco_formatado)
        if preco <= 0:
            return False, "O preço deve ser um valor positivo maior que zero."
        if preco > 100000:
            return False, "O preço informado excede o limite máximo permitido (R$ 100.000,00)."
    except ValueError:
        return False, "O preço deve ser um número válido (ex: 49.90 ou 49,90)."

    # Validação do Estoque
    try:
        estoque = int(estoque_str.strip())
        if estoque < 0:
            return False, "A quantidade em estoque não pode ser negativa."
        if estoque > 100000:
            return False, "A quantidade de estoque excede o limite máximo permitido (100.000)."
    except ValueError:
        return False, "O estoque deve ser um número inteiro válido."

    return True, {
        "nome": nome_limpo,
        "preco": round(preco, 2),
        "estoque": estoque
    }


def validar_carrinho_venda(carrinho):
    """Valida se há itens no carrinho antes de finalizar venda."""
    if not carrinho:
        return False, "O carrinho está vazio. Adicione ao menos um item."
    return True, ""