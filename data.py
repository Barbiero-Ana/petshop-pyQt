import sqlite3
import hashlib

DB_PATH = 'petshop.db'

# ---------- Criação das Tabelas ----------
def criar_tabela_usuarios():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        primeiro_nome TEXT NOT NULL,
        sobrenome TEXT NOT NULL,
        telefone TEXT NOT NULL,
        genero TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        tipo_usuario TEXT NOT NULL DEFAULT 'paciente',
        senha_temporaria INTEGER DEFAULT 0
    )
    ''')
    conn.commit()
    conn.close()

def criar_tabela_funcionarios():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_completo TEXT NOT NULL,
        idade INTEGER NOT NULL,
        genero TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        telefone TEXT,
        especialidade TEXT NOT NULL,
        is_veterinario INTEGER NOT NULL DEFAULT 0,
        crvet TEXT
    )
    ''')
    conn.commit()
    conn.close()

def criar_tabela_pets():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_email TEXT,
        nome TEXT,
        idade TEXT,
        raca TEXT,
        sexo TEXT,
        foto TEXT,
        FOREIGN KEY (usuario_email) REFERENCES usuarios(email)
    )
    ''')
    conn.commit()
    conn.close()

def criar_tabela_consultas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consultas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id INTEGER NOT NULL,
        dono_email TEXT NOT NULL,
        veterinario_id INTEGER NOT NULL,
        data_consulta TEXT NOT NULL,
        hora_consulta TEXT NOT NULL,
        FOREIGN KEY (pet_id) REFERENCES pets(id),
        FOREIGN KEY (dono_email) REFERENCES usuarios(email),
        FOREIGN KEY (veterinario_id) REFERENCES funcionarios(id)
    )
    ''')
    conn.commit()
    conn.close()

# ---------- Inserções ----------
def inserir_usuario(primeiro_nome, sobrenome, telefone, genero, email, senha_hash, is_admin=0, tipo_usuario='paciente', senha_temporaria=0):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO usuarios (primeiro_nome, sobrenome, telefone, genero, email, senha, is_admin, tipo_usuario, senha_temporaria)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (primeiro_nome, sobrenome, telefone, genero, email, senha_hash, is_admin, tipo_usuario, senha_temporaria))
    conn.commit()
    conn.close()

def inserir_funcionario(nome_completo, idade, genero, email, telefone, especialidade, is_veterinario, crvet=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO funcionarios (
        nome_completo, idade, genero, email, telefone, especialidade, is_veterinario, crvet
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        nome_completo, idade, genero, email, telefone, especialidade,
        1 if is_veterinario else 0,
        crvet if is_veterinario else None
    ))
    conn.commit()
    conn.close()

def inserir_pet(usuario_email, nome, idade, raca, sexo, foto):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO pets (usuario_email, nome, idade, raca, sexo, foto)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (usuario_email, nome, idade, raca, sexo, foto))
    conn.commit()
    conn.close()

def inserir_consulta(pet_id, dono_email, veterinario_id, data_consulta, hora_consulta):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO consultas (pet_id, dono_email, veterinario_id, data_consulta, hora_consulta)
    VALUES (?, ?, ?, ?, ?)
    ''', (pet_id, dono_email, veterinario_id, data_consulta, hora_consulta))
    conn.commit()
    conn.close()

# ---------- Buscas ----------
def buscar_usuario_por_email(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def buscar_nome_usuario(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT primeiro_nome FROM usuarios WHERE email = ?", (email,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def buscar_todos_usuarios():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, primeiro_nome, sobrenome, email FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

def buscar_pets_usuario(usuario_email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, idade, raca, foto FROM pets WHERE usuario_email = ?", (usuario_email,))
    pets = cursor.fetchall()
    conn.close()
    return pets

def buscar_todos_pets_com_id():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, raca FROM pets")
    pets = cursor.fetchall()
    conn.close()
    return pets

def buscar_usuarios_email_nome(termo_busca):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    termo_busca = f"%{termo_busca.lower()}%"
    cursor.execute("""
        SELECT email, primeiro_nome || ' ' || sobrenome AS nome_completo
        FROM usuarios
        WHERE LOWER(primeiro_nome) LIKE ? OR LOWER(sobrenome) LIKE ? OR LOWER(email) LIKE ?
    """, (termo_busca, termo_busca, termo_busca))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def buscar_pets_com_dono(termo_busca=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if termo_busca:
        termo_busca = f"%{termo_busca.lower()}%"
        cursor.execute('''
            SELECT pets.id, pets.nome, pets.idade, pets.raca, pets.sexo, pets.foto, usuarios.primeiro_nome
            FROM pets
            INNER JOIN usuarios ON pets.usuario_email = usuarios.email
            WHERE LOWER(pets.nome) LIKE ? OR LOWER(usuarios.primeiro_nome) LIKE ?
        ''', (termo_busca, termo_busca))
    else:
        cursor.execute('''
            SELECT pets.id, pets.nome, pets.idade, pets.raca, pets.sexo, pets.foto, usuarios.primeiro_nome
            FROM pets
            INNER JOIN usuarios ON pets.usuario_email = usuarios.email
        ''')
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def buscar_funcionarios_veterinarios(completo=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if completo:
        cursor.execute('''
        SELECT id, nome_completo, idade, genero, email, crvet, especialidade
        FROM funcionarios
        WHERE crvet IS NOT NULL AND crvet != ''
        ''')
    else:
        cursor.execute('''
        SELECT id, nome_completo, idade, genero, email, crvet
        FROM funcionarios
        WHERE crvet IS NOT NULL AND crvet != ''
        ''')
    resultados = cursor.fetchall()
    conn.close()
    return resultados


def buscar_consultas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT consultas.id, pets.nome, pets.raca,
           usuarios.primeiro_nome, usuarios.email, usuarios.telefone,
           funcionarios.nome_completo, funcionarios.idade, funcionarios.genero,
           funcionarios.crvet, funcionarios.especialidade,
           consultas.data_consulta, consultas.hora_consulta
    FROM consultas
    JOIN pets ON consultas.pet_id = pets.id
    JOIN usuarios ON consultas.dono_email = usuarios.email
    JOIN funcionarios ON consultas.veterinario_id = funcionarios.id
    ORDER BY consultas.data_consulta, consultas.hora_consulta
    ''')
    resultados = cursor.fetchall()
    conn.close()
    return resultados


# ---------- Atualizações ----------
def atualizar_senha_temporaria(email, nova_senha_hash):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE usuarios
        SET senha = ?, senha_temporaria = 0
        WHERE email = ?
    """, (nova_senha_hash, email))
    conn.commit()
    conn.close()

# ---------- Verificações ----------
def verificar_usuario(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT email, senha_temporaria FROM usuarios WHERE email = ?", (email,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# ---------- Exclusões ----------
def excluir_usuario_por_id(usuario_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    conn.close()

def excluir_pet_por_id(pet_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pets WHERE id = ?", (pet_id,))
    conn.commit()
    conn.close()

def excluir_consulta_por_id(consulta_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM consultas WHERE id = ?", (consulta_id,))
    conn.commit()
    conn.close()

# ---------- Inicialização ----------
def criar_usuario_admin_padrao():
    email_admin = "admin@petshop.com"
    senha_admin = "admin123"
    senha_hash = hashlib.sha256(senha_admin.encode()).hexdigest()

    if not buscar_usuario_por_email(email_admin):
        inserir_usuario(
            "Admin", "Master", "00000000000", "Outro",
            email_admin, senha_hash, is_admin=1, tipo_usuario='admin', senha_temporaria=0
        )
        print("Usuário administrador criado com sucesso.")
    else:
        print("Usuário administrador já existe.")

if __name__ == "__main__":
    criar_tabela_usuarios()
    criar_tabela_funcionarios()
    criar_tabela_pets()
    criar_tabela_consultas()
    criar_usuario_admin_padrao()
    print("Banco de dados inicializado com sucesso.")
