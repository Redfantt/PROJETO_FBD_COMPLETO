import psycopg2

# Função para estabelecer a conexão com o banco de dados
def conectar_bd():
    try:
        conexao = psycopg2.connect(
            host='localhost',
            port='5432',
            user='postgres',
            password='123',
            database='Hospedagem2'
        )
        return conexao
    except psycopg2.Error as e:
        print('Erro ao conectar ao banco de dados:', e)
        return None

# Função para verificar se as tabelas já existem
def tabelas_existentes():
    conexao = conectar_bd()
    if conexao is None:
        return False

    try:
        cursor = conexao.cursor()

        # Verificar se as tabelas CLIENTE, CONSUMO e QUARTO já existem
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name IN ('cliente', 'consumo', 'quarto')
        """)
        resultado = cursor.fetchone()

        return resultado[0] == 3  # Retorna True se as 3 tabelas existirem

    except psycopg2.Error as e:
        print('Erro ao verificar tabelas existentes:', e)
        return False

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

# Função para criar as tabelas
def criar_tabelas():
    if tabelas_existentes():
        print('As tabelas já existem.')
        return

    conexao = conectar_bd()
    if conexao is None:
        return

    try:
        cursor = conexao.cursor()

        # Criar tabela CLIENTE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CLIENTE (
                ID_CLIENTE SERIAL PRIMARY KEY,
                NOME VARCHAR(255) NOT NULL,
                CPF VARCHAR(11) NOT NULL UNIQUE, -- Adicionando UNIQUE ao campo CPF
                TELEFONE VARCHAR(20) NOT NULL
            );
        """)

        # Criar tabela QUARTO
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS QUARTO (
                ID_QUARTO SERIAL PRIMARY KEY,
                NUM_QUARTO INT UNIQUE,
                NUM_CAMAS INT NOT NULL,
                NUM_BANHEIROS INT NOT NULL,
                STATUS VARCHAR(20) NOT NULL,
                DIARIA DECIMAL(10, 2) NOT NULL
            );
        """)

        # Criar tabela HOSPEDAGEM
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS HOSPEDAGEM (
                id SERIAL PRIMARY KEY,
                cliente_id INTEGER NOT NULL,
                quarto_id INTEGER NOT NULL,
                num_dias INTEGER NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES cliente(ID_CLIENTE),
                FOREIGN KEY (quarto_id) REFERENCES quarto(ID_QUARTO)
            );
        """)

        conexao.commit()
        print('Tabelas criadas com sucesso.')

    except psycopg2.Error as e:
        print('Erro ao criar tabelas:', e)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

# Chamar a função para criar as tabelas
criar_tabelas()