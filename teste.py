import psycopg2

from criar_tabelas import criar_tabelas, conectar_bd

# Restante do código para criar as tabelas...

# Chamar a função para criar as tabelas
criar_tabelas()

# Verificar se a tabela "Reservas" foi criada corretamente
def verificar_tabela_reservas():
    conexao = conectar_bd()
    if conexao is None:
        return

    try:
        cursor = conexao.cursor()

        # Consultar a tabela "Reservas"
        cursor.execute("""
            SELECT * FROM Reservas;
        """)
        reservas = cursor.fetchall()

        if reservas:
            print("Tabela 'Reservas' criada com sucesso.")
            print("Registros na tabela 'Reservas':")
            for reserva in reservas:
                print(reserva)
        else:
            print("A tabela 'Reservas' foi criada, mas ainda não contém registros.")

    except psycopg2.Error as e:
        print("Erro ao verificar tabela 'Reservas':", e)

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

# Chamar a função para verificar a tabela "Reservas"
verificar_tabela_reservas()
