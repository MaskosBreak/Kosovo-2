def validar_estoque_disponivel(produto):
    """Verifica se o produto tem estoque disponível."""
    if not produto:
        return False, "Produto não encontrado."
    if produto["estoque"] <= 0:
        return False, "Produto fora de estoque!"
    return True, ""


def validar_carrinho_nao_vazio(carrinho):
    """Verifica se o carrinho contém itens para finalizar a compra."""
    if not carrinho:
        return False, "O carrinho está vazio."
    return True, ""