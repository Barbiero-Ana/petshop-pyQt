import hashlib
from data import inserir_usuario, buscar_usuario_por_email

def cadastrar_usuario(dados):
    for campo, valor in dados.items():
        if not valor or valor.strip() == '':
            return False, f"Campo {campo} não pode estar vazio"

    telefone = dados.get('telefone')
    if not validar_telefone(telefone):
        return False, "Telefone inválido, use formato (XX)XXXXX-XXXX"

    if buscar_usuario_por_email(dados.get('email')):
        return False, "Email já cadastrado"

    if dados.get('senha') != dados.get('repetirsenha'):
        return False, "Senhas não conferem"

    senha_hash = hashlib.sha256(dados.get('senha').encode('utf-8')).hexdigest()

    inserir_usuario(
        dados['primeironome'],
        dados['sobrenome'],
        dados['telefone'],
        dados['genero'],
        dados['email'],
        senha_hash
    )

    return True, "Usuário cadastrado com sucesso"

def validar_telefone(telefone):
    import re
    pattern = r'^\(\d{2}\)\d{4,5}-\d{4}$'
    return bool(re.match(pattern, telefone))

def logar_usuario(email, senha):
    usuario = buscar_usuario_por_email(email)
    if not usuario:
        return False, "Usuário não encontrado", False

    senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
    senha_banco = usuario[6]
    is_admin = usuario[7] if len(usuario) > 7 else 0  # garante compatibilidade

    if senha_hash == senha_banco:
        return True, "Login realizado com sucesso", bool(is_admin)
    else:
        return False, "Senha incorreta", False
