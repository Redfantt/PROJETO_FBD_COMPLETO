from flask import Flask, render_template, request, redirect, session
import psycopg2
from criar_tabelas import criar_tabelas

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta'  # Chave secreta para sessões


# Função auxiliar para estabelecer a conexão com o banco de dados
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


# Rota de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session and session['logged_in']:
        return redirect('/opcoes')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'luiz' and password == '123':
            session['logged_in'] = True
            return redirect('/opcoes')
        else:
            return render_template('login.html', error='Credenciais inválidas')
    return render_template('login.html', error='')


# Rota de logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')


# Rota das opções
@app.route('/opcoes')
def opcoes():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('opcoes.html')


# Rota de cadastro de cliente

@app.route('/cadastrar_cliente', methods=['POST'])
def cadastrar_cliente():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        telefone = request.form['telefone']

        conexao = conectar_bd()
        if conexao:
            cursor = conexao.cursor()

            # Verificar se o cliente já está cadastrado
            query = "SELECT COUNT(*) FROM cliente WHERE cpf = %s"
            cursor.execute(query, (cpf,))
            resultado = cursor.fetchone()

            if resultado[0] == 0:
                # Cliente não existe, então cadastrar
                query = "INSERT INTO cliente (nome, cpf, telefone) VALUES (%s, %s, %s)"
                cursor.execute(query, (nome, cpf, telefone))
                conexao.commit()
                cursor.close()
                conexao.close()

                # Enviar mensagem de sucesso
                return render_template('cliente.html', mensagem_cadastro='Cliente cadastrado com sucesso.')

            else:
                # Cliente já existe, exibir mensagem de erro
                cursor.close()
                conexao.close()
                return render_template('cliente.html', mensagem_cadastro='Erro: CPF já cadastrado.')

    return redirect('/cliente')


# Rota de busca de cliente
@app.route('/buscar_cliente', methods=['GET'])
def buscar_cliente():
    if not session.get('logged_in'):
        return redirect('/')

    cpf = request.args.get('cpf')

    conexao = conectar_bd()
    if conexao:
        cursor = conexao.cursor()
        query = "SELECT * FROM cliente WHERE cpf = %s"
        cursor.execute(query, (cpf,))
        cliente = cursor.fetchone()
        cursor.close()
        conexao.close()

        if cliente:
            # Se o cliente foi encontrado, exibir seus dados usando o template cliente_encontrado.html
            return render_template('cliente_encontrado.html', cliente=cliente)
        else:
            # Se o cliente não foi encontrado, exibir a mensagem de erro na página cliente.html
            return render_template('cliente.html', mensagem_buscar='Erro: CPF não encontrado.')

    return redirect('/cliente')


# Rota de atualização de cliente
@app.route('/editar_cliente', methods=['POST'])
def editar_cliente():
    if not session.get('logged_in'):
        return redirect('/')

    cpf = request.form['cpf']
    novo_cpf = request.form['novo_cpf']
    nome = request.form['novo_nome']
    telefone = request.form['novo_telefone']

    conexao = conectar_bd()
    if conexao:
        cursor = conexao.cursor()
        query = "SELECT * FROM cliente WHERE cpf = %s"
        cursor.execute(query, (cpf,))
        cliente_encontrado = cursor.fetchone()

        if cliente_encontrado is None:
            mensagem = 'Cliente não encontrado.'
        else:
            if novo_cpf != cpf:
                # Verificando se o novo CPF já existe na base de dados
                query = "SELECT * FROM cliente WHERE cpf = %s"
                cursor.execute(query, (novo_cpf,))
                cliente_com_novo_cpf = cursor.fetchone()
                if cliente_com_novo_cpf:
                    return render_template('cliente.html', mensagem_editar='O novo CPF já existe.')

            query = "UPDATE cliente SET nome = %s, cpf = %s, telefone = %s WHERE cpf = %s"
            cursor.execute(query, (nome, novo_cpf, telefone, cpf))
            conexao.commit()
            mensagem = 'Cliente editado com sucesso.'

        cursor.close()
        conexao.close()

    return render_template('cliente.html', mensagem_editar=mensagem)


# Rota de remoção de cliente
@app.route('/remover_cliente', methods=['POST'])
def remover_cliente():
    if not session.get('logged_in'):
        return redirect('/')
    if request.method == 'POST':
        cpf = request.form['cpf']

        conexao = conectar_bd()
        if conexao:
            cursor = conexao.cursor()

            # Verificar se o cliente com o CPF informado existe
            query = "SELECT COUNT(*) FROM cliente WHERE cpf = %s"
            cursor.execute(query, (cpf,))
            resultado = cursor.fetchone()

            if resultado[0] > 0:
                # Cliente encontrado, então remova
                query = "DELETE FROM cliente WHERE cpf = %s"
                cursor.execute(query, (cpf,))
                conexao.commit()
                cursor.close()
                conexao.close()

                # Enviar mensagem de sucesso
                return render_template('cliente.html', mensagem_remover='Cliente removido com sucesso.')

            else:
                # Cliente não encontrado, exibir mensagem de erro
                cursor.close()
                conexao.close()
                return render_template('cliente.html', mensagem_remover='Erro: CPF não encontrado.')

    return redirect('/cliente')


# Rota de cliente
@app.route('/cliente')
def cliente():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('cliente.html')


# Rota para a página de opções
@app.route('/opcoes.html')
def opcoes_html():
    return render_template('opcoes.html')



# Rota de quarto
@app.route('/quarto')
def quarto():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('quarto.html')




# Função para obter a lista de quartos cadastrados
def obter_lista_quartos():
    conexao = conectar_bd()
    if conexao is None:
        return []

    try:
        cursor = conexao.cursor()

        # Obter todos os quartos cadastrados
        cursor.execute("SELECT * FROM quarto")
        lista_quartos = cursor.fetchall()

        return lista_quartos

    except psycopg2.Error as e:
        print('Erro ao obter a lista de quartos:', e)
        return []

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# Rota de cadastro de quarto
@app.route('/cadastrar_quarto', methods=['POST'])
def cadastrar_quarto():
    if not session.get('logged_in'):
        return redirect('/')

    mensagem_cadastro = None

    if request.method == 'POST':
        num_quarto = request.form['num_quarto']
        num_camas = request.form['num_camas']
        num_banheiros = request.form['num_banheiros']
        status = request.form['status']
        diaria = request.form['diaria']

        conexao = conectar_bd()
        if conexao:
            cursor = conexao.cursor()

            # Verificar se o quarto com o número informado já existe
            query = "SELECT COUNT(*) FROM quarto WHERE num_quarto = %s"
            cursor.execute(query, (num_quarto,))
            resultado = cursor.fetchone()

            if resultado[0] == 0:
                # Quarto não existe, então cadastrar
                query = "INSERT INTO quarto (num_quarto, num_camas, num_banheiros, status, diaria) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (num_quarto, num_camas, num_banheiros, status, diaria))
                conexao.commit()
                cursor.close()
                conexao.close()

                # Atualizar a lista de quartos
                lista_quartos = obter_lista_quartos()

                # Definir a mensagem de sucesso
                mensagem_cadastro = 'Quarto cadastrado com sucesso.'
            else:
                # Quarto já existe, exibir mensagem de erro
                mensagem_cadastro = 'Erro: Já existe um quarto com este número.'

    # Recarregar a lista de quartos
    lista_quartos = obter_lista_quartos()

    return render_template('quarto.html', lista_quartos=lista_quartos, mensagem_cadastro=mensagem_cadastro)


# Rota de ocupar/quitar quarto
@app.route('/ocupar_quarto', methods=['GET', 'POST'])
def ocupar_quarto():
    if not session.get('logged_in'):
        return redirect('/')

    # Carregar a lista de quartos existentes
    lista_quartos = obter_lista_quartos()

    if request.method == 'POST':
        num_quarto = request.form['num_quarto']
        status = request.form.get('status')

        conexao = conectar_bd()
        if conexao:
            cursor = conexao.cursor()

            # Verificar se o quarto com o número informado existe
            query = "SELECT COUNT(*) FROM quarto WHERE num_quarto = %s"
            cursor.execute(query, (num_quarto,))
            resultado = cursor.fetchone()

            if resultado[0] > 0:
                # O quarto existe, atualizar o status
                query = "UPDATE quarto SET status = %s WHERE num_quarto = %s"
                cursor.execute(query, (status, num_quarto))
                conexao.commit()
                cursor.close()
                conexao.close()

                # Enviar mensagem de sucesso
                mensagem_ocupar = 'Status do quarto atualizado com sucesso.'
                lista_quartos = obter_lista_quartos()
                return render_template('quarto.html', lista_quartos=lista_quartos, mensagem_ocupar=mensagem_ocupar)

            else:
                # Quarto não encontrado, exibir mensagem de erro
                mensagem_ocupar = 'Erro: Quarto não encontrado.'

    return render_template('quarto.html', lista_quartos=lista_quartos)

# ... Outras rotas e imports ...

# Rota de hospedagem
@app.route('/hospedagem', methods=['GET', 'POST'])
def hospedagem():
    if not session.get('logged_in'):
        return redirect('/')

    mensagem = None  # Inicialmente, não há mensagem

    if request.method == 'POST':
        cpf = request.form['cpf']
        num_quarto = int(request.form['num_quarto'])
        num_dias = int(request.form['num_dias'])

        # Verificar se o cliente com o CPF informado existe
        conexao = conectar_bd()
        if conexao:
            cursor = conexao.cursor()

            # Verificar se o cliente com o CPF informado existe
            query = "SELECT ID_CLIENTE FROM cliente WHERE cpf = %s"
            cursor.execute(query, (cpf,))
            cliente_id = cursor.fetchone()

            if not cliente_id:
                # Cliente não existe, definir a mensagem de erro
                mensagem = 'Erro: Não existe cliente com esse CPF cadastrado.'
            else:
                cliente_id = cliente_id[0]

                # Verificar se o quarto com o número informado existe e está disponível
                query = "SELECT ID_QUARTO, STATUS FROM quarto WHERE NUM_QUARTO = %s"
                cursor.execute(query, (num_quarto,))
                quarto_info = cursor.fetchone()

                if not quarto_info:
                    # Quarto não existe, definir a mensagem de erro
                    mensagem = 'Erro: Não existe quarto com esse número cadastrado.'
                else:
                    quarto_id, status_quarto = quarto_info

                    if status_quarto == 'livre':
                        # Realizar a hospedagem, criando um registro na tabela "hospedagem"
                        query = "INSERT INTO hospedagem (cliente_id, quarto_id, num_dias) VALUES (%s, %s, %s)"
                        cursor.execute(query, (cliente_id, quarto_id, num_dias))

                        conexao.commit()

                        # Atualizar o status do quarto para "ocupado"
                        query = "UPDATE quarto SET STATUS = 'ocupado' WHERE ID_QUARTO = %s"
                        cursor.execute(query, (quarto_id,))
                        conexao.commit()

                        # Definir a mensagem de sucesso
                        mensagem = 'Hospedagem realizada com sucesso. Quarto agora está ocupado.'
                    else:
                        # Quarto não está disponível para hospedagem, definir a mensagem de erro
                        mensagem = 'Erro: O quarto não está disponível para hospedagem.'

            cursor.close()
            conexao.close()

    return render_template('hospedagem.html', mensagem=mensagem)



# Rota para quitar hospedagem
@app.route('/quitar_hospedagem', methods=['POST'])
def quitar_hospedagem():
    if not session.get('logged_in'):
        return redirect('/')

    mensagem_quitar = None  # Inicialmente, não há mensagem de quitação
    cliente_info = None     # Inicialmente, não há informações do cliente

    if request.method == 'POST':
        cpf = request.form['cpf']
        num_quarto = int(request.form['num_quarto'])

        # Verificar se a hospedagem com o CPF e número do quarto informados existe
        conexao = conectar_bd()
        if conexao:
            cursor = conexao.cursor()

            # Verificar se a hospedagem existe e obter os dados necessários
            query = "SELECT cliente.nome, cliente.cpf, quarto.NUM_QUARTO, " \
                    "hospedagem.num_dias, quarto.DIARIA " \
                    "FROM hospedagem " \
                    "JOIN cliente ON hospedagem.cliente_id = cliente.ID_CLIENTE " \
                    "JOIN quarto ON hospedagem.quarto_id = quarto.ID_QUARTO " \
                    "WHERE cliente.cpf = %s AND quarto.NUM_QUARTO = %s"
            cursor.execute(query, (cpf, num_quarto))
            hospedagem_info = cursor.fetchone()

            if not hospedagem_info:
                # A hospedagem não existe, definir a mensagem de erro
                mensagem_quitar = 'Erro: Não existe hospedagem associada a esse CPF e número do quarto.'
            else:
                nome, cpf_cliente, num_quarto, num_dias, valor_diaria = hospedagem_info
                valor_total = valor_diaria * num_dias

                # Atualizar o status do quarto para "livre"
                query = "UPDATE quarto SET STATUS = 'livre' WHERE NUM_QUARTO = %s"
                cursor.execute(query, (num_quarto,))
                conexao.commit()

                # Excluir o registro da tabela "hospedagem"
                query = "DELETE FROM hospedagem WHERE cliente_id = (SELECT ID_CLIENTE FROM cliente WHERE cpf = %s) " \
                        "AND quarto_id = (SELECT ID_QUARTO FROM quarto WHERE NUM_QUARTO = %s)"
                cursor.execute(query, (cpf, num_quarto))
                conexao.commit()

                # Definir as informações do cliente para exibir na "nota fiscal"
                cliente_info = {
                    'nome': nome,
                    'cpf': cpf_cliente,
                    'num_quarto': num_quarto,
                    'num_dias': num_dias,
                    'valor_diaria': valor_diaria,
                    'valor_total': valor_total
                }

                # Definir a mensagem de sucesso
                mensagem_quitar = f'A hospedagem de: {nome}\nCPF: {cpf_cliente}\nNo quarto de número: {num_quarto}\n' \
                                  f'Hospedado por: {num_dias} dias\nValor da diária: R$ {valor_diaria:.2f}\n' \
                                  f'Valor total a pagar: R$ {valor_total:.2f}\nHospedagem quitada com sucesso.'

            cursor.close()
            conexao.close()

    return render_template('quitar_hospedagem.html', mensagem_quitar=mensagem_quitar, cliente_info=cliente_info)


@app.route('/listar_hospedagens')
def listar_hospedagens():
    if not session.get('logged_in'):
        return redirect('/')

    conexao = conectar_bd()
    hospedagens = []

    if conexao:
        cursor = conexao.cursor()

        # Consultar as informações dos clientes hospedados
        query = "SELECT cliente.nome, cliente.cpf, quarto.NUM_QUARTO, hospedagem.num_dias, quarto.DIARIA " \
                "FROM hospedagem " \
                "JOIN cliente ON hospedagem.cliente_id = cliente.ID_CLIENTE " \
                "JOIN quarto ON hospedagem.quarto_id = quarto.ID_QUARTO"
        cursor.execute(query)
        hospedagens = cursor.fetchall()

        cursor.close()
        conexao.close()

    return render_template('listar_hospedagens.html', hospedagens=hospedagens)

@app.route('/listar_quartos')
def listar_quartos():
    # Conectar ao banco de dados e obter os quartos cadastrados
    conexao = conectar_bd()
    if conexao:
        cursor = conexao.cursor()

        # Consultar os quartos cadastrados
        query = "SELECT NUM_QUARTO, NUM_CAMAS, NUM_BANHEIROS, STATUS, DIARIA FROM quarto"
        cursor.execute(query)
        quartos = cursor.fetchall()

        cursor.close()
        conexao.close()

        return render_template('listar_quartos.html', quartos=quartos)
    else:
        return render_template('listar_quartos.html', quartos=None)

#Cancelando a hospedagem
@app.route('/cancelar_hospedagem', methods=['POST'])
def cancelar_hospedagem():
    cpf = request.form['cpf']

    conexao = conectar_bd()
    if conexao:
        cursor = conexao.cursor()

        # Verificar se o cliente com o CPF informado existe
        query = "SELECT ID_CLIENTE FROM cliente WHERE CPF = %s"
        cursor.execute(query, (cpf,))
        cliente_id = cursor.fetchone()

        if not cliente_id:
            mensagem_cancelar = 'Cliente não está hospedado.'
        else:
            cliente_id = cliente_id[0]

            # Obter o ID do quarto onde o cliente está hospedado
            query = "SELECT quarto_id FROM hospedagem WHERE cliente_id = %s"
            cursor.execute(query, (cliente_id,))
            quarto_id = cursor.fetchone()

            if quarto_id:
                quarto_id = quarto_id[0]

                # Atualizar o status do quarto para "livre"
                query = "UPDATE quarto SET STATUS = 'livre' WHERE ID_QUARTO = %s"
                cursor.execute(query, (quarto_id,))

                # Excluir o registro da hospedagem cancelada da tabela "hospedagem"
                query = "DELETE FROM hospedagem WHERE cliente_id = %s"
                cursor.execute(query, (cliente_id,))

                conexao.commit()
                mensagem_cancelar = 'O cancelamento da hospedagem do cliente foi feito com sucesso!'
            else:
                mensagem_cancelar = 'Cliente não está hospedado.'

        cursor.close()
        conexao.close()

    return render_template('hospedagem.html', mensagem_cancelar=mensagem_cancelar)





if __name__ == '__main__':
    criar_tabelas()  # Chamar a função para
    app.run(debug=True)
