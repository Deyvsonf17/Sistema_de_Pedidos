from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave_super_secreta'

# Configuração da conexão com o PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pedido2:pedido2@localhost:5544/pedido2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para Usuários
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.Text, nullable=False)
    telefone = db.Column(db.String(15), nullable=False)

# Modelo para Pedidos
class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo_galeto = db.Column(db.String(50), nullable=True)
    tipo_pedido = db.Column(db.String(100), nullable=False)
    carne = db.Column(db.String(100), nullable=True)  # Permitindo carne como nulo
    feijao = db.Column(db.String(50), nullable=True)  # Permitindo feijão como nulo
    acompanhamentos = db.Column(db.Text, nullable=True)
    quantidade = db.Column(db.Integer, nullable=False)
    forma_pagamento = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Pedido Recebido")
    troco_para = db.Column(db.Float, nullable=True)
    total = db.Column(db.Float, nullable=False)
    observacao = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    # Relacionamento com a tabela Usuario
    usuario = db.relationship('Usuario', backref=db.backref('pedidos', lazy=True))

# Criar tabelas
with app.app_context():
    db.create_all()

# Rota para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and check_password_hash(usuario.password, password):
            session['user_id'] = usuario.id
            return redirect('/')
        return "Nome de usuário ou senha incorretos."
    return render_template('login.html')

# Rota para criar conta
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nome = request.form['nome']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        existing_user = Usuario.query.filter_by(username=username).first()
        if existing_user:
            return "Nome de usuário já existe, escolha outro."

        novo_usuario = Usuario(nome=nome, endereco=endereco, telefone=telefone, username=username, password=password)
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect('/login')
    return render_template('signup.html')

# Rota para logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

# Rota principal (Home)
@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('cliente.html', page='home')
    else:
        return redirect('/login')

# Rota para fazer pedido
@app.route('/pedido', methods=['GET', 'POST'])
def pedido():
    if 'user_id' not in session:
        return redirect('/login')

    tipo_pedido = request.args.get('tipo')

    if request.method == 'POST':
        usuario = Usuario.query.get(session['user_id'])
        quantidade = int(request.form['quantidade'])
        observacao = request.form.get('observacao')  # Pegando o valor da observação

        # Pedido do tipo Comercial
        if tipo_pedido == 'comercial':
            carne = request.form.get('carne')  # Usando get() para evitar o KeyError
            feijao = request.form.get('feijao')
            total = quantidade * 18  # Valor fixo para Comercial

            novo_pedido = Pedido(
                tipo_pedido='Comercial',
                carne=carne,
                feijao=feijao,
                quantidade=quantidade,
                total=total,
                usuario_id=usuario.id,
                forma_pagamento="Pendente",
                observacao=observacao  # Salvando a observação no pedido
            )

        # Pedido do tipo Galeto
        elif tipo_pedido == 'galeto':
            tipo_galeto = request.form.get('tipo_galeto')
            feijao = request.form.get('feijao') if tipo_galeto != 'simples' else None

            if tipo_galeto == 'simples':
                acompanhamentos = "Farofa, Vinagrete e Batata Frita"
                total = quantidade * 40
            elif tipo_galeto == 'meio':
                acompanhamentos = "Arroz, Feijão, Farofa, Vinagrete e Batata Frita"
                total = quantidade * 29
            else:  # Galeto completo
                acompanhamentos = "Arroz, Feijão, Farofa, Vinagrete e Batata Frita"
                total = quantidade * 50

            novo_pedido = Pedido(
                tipo_pedido='Galeto',
                tipo_galeto=tipo_galeto,
                feijao=feijao,
                acompanhamentos=acompanhamentos,
                quantidade=quantidade,
                total=total,
                usuario_id=usuario.id,
                forma_pagamento="Pendente",
                observacao=observacao  # Salvando a observação no pedido
            )

        # Pedido do tipo Executivo
        elif tipo_pedido == 'executivo':
            prato_executivo = request.form.get('prato_executivo')
            feijao = None if prato_executivo in ['parmegiana_carne', 'parmegiana_camarao', 'parmegiana_frango'] else request.form.get('feijao')
            acompanhamentos = "Arroz, Macarrão, Farofa, Vinagrete e Batata Frita" if prato_executivo != 'parmegiana' else "Macarrão e Batata Frita"
            precos = {
                'pernil_suino': 30,
                'file_bode': 32,
                'carne_sol': 30,
                'maminha': 30,
                'picanha_suina': 32,
                'carneiro': 32,
                'picanha_nacional': 32,
                'meio_galeto': 29,
                'charque': 30,
                'parmegiana_carne': 25,
                'parmegiana_camarao': 30,
                'parmegiana_frango': 23,
            }
            total = quantidade * precos[prato_executivo]

            novo_pedido = Pedido(
                tipo_pedido='Executivo',
                carne=prato_executivo,
                feijao=feijao,
                acompanhamentos=acompanhamentos,
                quantidade=quantidade,
                total=total,
                usuario_id=usuario.id,
                forma_pagamento="Pendente",
                observacao=observacao  # Salvando a observação no pedido
            )

        db.session.add(novo_pedido)
        db.session.commit()

        if 'adicionar_pedido' in request.form:  # Verifica se o usuário clicou em "Adicionar mais pedido"
            return redirect('/')

        return redirect('/pagamento')

    return render_template('cliente.html', page='pedido', tipo_pedido=tipo_pedido)

# Rota para pagamento
@app.route('/pagamento', methods=['GET', 'POST'])
def realizar_pagamento():
    if 'user_id' not in session:
        return redirect('/login')

    # Recupera o pedido do usuário
    pedido = Pedido.query.filter_by(usuario_id=session['user_id'], forma_pagamento="Pendente").order_by(Pedido.id.desc()).first()
    
    if not pedido:
        return "Nenhum pedido encontrado.", 404

    if request.method == 'POST':
        try:
            # Recupera a forma de pagamento
            forma_pagamento = request.form.get('forma_pagamento')
            if not forma_pagamento:
                return "Forma de pagamento não selecionada.", 400

            # Atualiza o pedido com a forma de pagamento
            pedido.forma_pagamento = forma_pagamento

            troco_para = None  # Inicializa troco_para como None

            # Processamento para pagamento em dinheiro
            if forma_pagamento == 'dinheiro':
                precisa_troco = request.form.get('precisa_troco', 'não')  # Assume 'não' se não for informado
                if precisa_troco == 'sim':
                    troco_para = request.form.get('troco')
                    if not troco_para:
                        return "Informe o valor para o troco.", 400
                    try:
                        troco_para = float(troco_para)
                    except ValueError:
                        return "Valor de troco inválido.", 400

                    if troco_para < pedido.total:
                        return "O valor do troco não pode ser menor que o total a pagar.", 400
                    pedido.troco_para = troco_para
                else:
                    pedido.troco_para = None

                mensagem_confirmacao = "O entregador levará seu pedido em breve. Acompanhe o status pelo site."

            # Processamento para pagamento via Pix
            elif forma_pagamento == 'pix':
                nome_pagador_pix = request.form.get('nome_pagador_pix')
                if not nome_pagador_pix:
                    return "Nome do pagador do Pix é obrigatório.", 400

                mensagem_confirmacao = f"O pedido será preparado e entregue em breve. Nome do pagador do Pix: {nome_pagador_pix}. Acompanhe o status pelo site."

            # Processamento para pagamento no cartão
            elif forma_pagamento == 'cartao':
                mensagem_confirmacao = "O entregador levará a maquineta e o pedido será entregue em breve. Acompanhe o status pelo site."

            # Adiciona a taxa de entrega ao total
            pedido.total += 5  # Taxa de entrega
            db.session.commit()

            # Passa 'None' se não houver troco
            return render_template('cliente.html', page='confirmacao_pagamento', total=pedido.total, forma_pagamento=forma_pagamento, mensagem_confirmacao=mensagem_confirmacao, troco_para=troco_para, pedido=pedido)

        except Exception as e:
            print(f"Erro na rota de pagamento: {e}")  # Log no servidor
            return "Ocorreu um erro ao processar o pagamento. Tente novamente.", 500

    # Para a requisição GET, renderiza o template de pagamento com o pedido
    return render_template('cliente.html', page='pagamento', pedido=pedido)











# Rota para histórico de pedidos
@app.route('/historico')
def historico():
    if 'user_id' not in session:
        return redirect('/login')

    # Filtra pedidos com pagamento finalizado
    pedidos = Pedido.query.filter_by(usuario_id=session['user_id']).filter(Pedido.forma_pagamento != 'Pendente').all()
    return render_template('cliente.html', page='historico', pedidos=pedidos)






# Rota para cancelar pedido
@app.route('/cancelar_pedido/<int:pedido_id>', methods=['POST'])
def cancelar_pedido(pedido_id):
    if 'user_id' not in session:
        return redirect('/login')

    # Tenta encontrar o pedido no banco de dados
    pedido = Pedido.query.get(pedido_id)

    if not pedido:
        return "Pedido não encontrado.", 404

    # Verifica se o pedido pertence ao usuário logado
    if pedido.usuario_id != session['user_id']:
        return "Você não tem permissão para cancelar este pedido.", 403

    # Exclui o pedido
    db.session.delete(pedido)
    db.session.commit()

    return redirect('/status_pedido')  # Redireciona para a página de status de pedidos após o cancelamento





# Rota para status do pedido
@app.route('/status_pedido')
def status_pedido():
    if 'user_id' not in session:
        return redirect('/login')

    # Filtra pedidos com status diferente de "Entregue" e com pagamento finalizado
    pedidos = Pedido.query.filter_by(usuario_id=session['user_id']).filter(Pedido.status != 'Entregue').filter(Pedido.forma_pagamento != 'Pendente').order_by(Pedido.id.desc()).all()
    
    return render_template('cliente.html', page='status_pedido', pedidos=pedidos)

# Rota para administração
@app.route('/admin')
def admin():
    pedidos = Pedido.query.all()
    return render_template('admin.html', pedidos=pedidos)

# Rota para alterar status do pedido
@app.route('/alterar_status_ajax/<int:pedido_id>', methods=['POST'])
def alterar_status_ajax(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    
    if not pedido:
        return "Pedido não encontrado", 404
    
    novo_status = request.form['status']
    
    # Atualiza o status do pedido
    pedido.status = novo_status
    db.session.commit()
    
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
