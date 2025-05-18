from flask import abort, flash, Blueprint, render_template, request, redirect, url_for, session
from app import db
from app.models import Usuario, Produto, Mensagem, Historico
from sqlalchemy.orm import joinedload
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

main = Blueprint('main', __name__)

def extensao_permitida(nome):
    return '.' in nome and nome.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'erro')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def registrar_acao(id_usuario, acao, produto=None, destinatario=None):
    registro = Historico(
        id_usuario=id_usuario,
        acao=acao,
        produto=produto,
        destinatario=destinatario,
        data_hora=datetime.utcnow()
    )
    db.session.add(registro)
    db.session.commit()


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email, senha=senha).first()
        if usuario:
            session['usuario_id'] = usuario.id
            session['nome'] = usuario.nome
            return redirect(url_for('main.painel'))
        flash('Usuário ou senha inválidos')
    return render_template('login.html', mostrar_apenas_sair=True, ocultar_botao_produtos=True, ocultar_inicio=True)

@main.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'sucesso')
    return redirect(url_for('main.login'))

@main.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        confirmar = request.form['confirmar']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        foto = request.files.get('foto')

        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está em uso.', 'erro')
            return redirect(url_for('main.cadastro'))

        if senha != confirmar:
            flash('As senhas não coincidem.', 'erro')
            return redirect(url_for('main.cadastro'))

        nome_arquivo = None
        if foto and extensao_permitida(foto.filename):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            nome_arquivo = f"{uuid.uuid4().hex}_{secure_filename(foto.filename)}"
            caminho_foto = os.path.join(UPLOAD_FOLDER, nome_arquivo)
            foto.save(caminho_foto)

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha,
            endereco=endereco,
            telefone=telefone,
            foto=nome_arquivo
        )
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso!', 'sucesso')
        return redirect(url_for('main.login'))

    return render_template('cadastro.html', mostrar_botoes_direita=True)

@main.route('/painel')
@login_required
def painel():
    return render_template('painel.html')

@main.route('/produto/novo', methods=['GET', 'POST'])
@login_required
def cadastrar_produto():
    if request.method == 'POST':
        dados = request.form
        tipo = ','.join(dados.getlist('tipo'))
        imagem = request.files.get('imagem')
        nome_arquivo = None

        if imagem and imagem.filename:
            if extensao_permitida(imagem.filename):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                nome_arquivo = f"{uuid.uuid4().hex}_{secure_filename(imagem.filename)}"
                imagem.save(os.path.join(UPLOAD_FOLDER, nome_arquivo))
            else:
                flash('Formato de imagem não permitido.')
                return redirect(request.url)

        novo = Produto(
            nome=dados.get('nome'),
            descricao=dados.get('descricao'),
            categoria=dados.get('categoria'),
            condicao=dados.get('condicao'),
            tipo=tipo,
            imagem=nome_arquivo,
            id_usuario=session['usuario_id'],
            localizacao=dados.get('localizacao'),
            data_cadastro=datetime.today().date(),
            estado_conservacao=dados.get('estado_conservacao'),
            altura=dados.get('altura'),
            largura=dados.get('largura'),
            profundidade=dados.get('profundidade'),
            voltagem=dados.get('voltagem'),
            nivel_ruido=dados.get('nivel_ruido'),
            sistema=dados.get('sistema'),
            observacoes=dados.get('observacoes'),
            disponivel=True
        )
        db.session.add(novo)
        db.session.commit()
        registrar_acao(session['usuario_id'], 'Produto anunciado', dados.get('nome'))
        flash('Produto cadastrado com sucesso!')
        return redirect(url_for('main.painel'))

    # Exibe a página com os botões corretos
    return render_template(
        'cadastro_produto.html',
        mostrar_apenas_sair=True,
        ocultar_inicio=False,
        ocultar_botao_produtos=False
    )



@main.route('/produto/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_produto(id):
    produto = Produto.query.get_or_404(id)

    if produto.id_usuario != session.get('usuario_id'):
        flash('Você não tem permissão para editar este produto.')
        return redirect(url_for('main.list_produtos'))

    if request.method == 'POST':
        produto.nome = request.form.get('nome')
        produto.descricao = request.form.get('descricao')
        produto.categoria = request.form.get('categoria')
        produto.localizacao = request.form.get('localizacao')
        produto.estado_conservacao = request.form.get('estado_conservacao')
        produto.altura = request.form.get('altura')
        produto.largura = request.form.get('largura')
        produto.profundidade = request.form.get('profundidade')
        produto.voltagem = request.form.get('voltagem')
        produto.nivel_ruido = request.form.get('nivel_ruido')
        produto.sistema = request.form.get('sistema')
        produto.observacoes = request.form.get('observacoes')
        produto.condicao = request.form.get('condicao')
        produto.tipo = ','.join(request.form.getlist('tipo'))

        nova_imagem = request.files.get('imagem')
        if nova_imagem and nova_imagem.filename:
            if extensao_permitida(nova_imagem.filename):
                if produto.imagem:
                    caminho_antigo = os.path.join(UPLOAD_FOLDER, produto.imagem)
                    if os.path.exists(caminho_antigo):
                        os.remove(caminho_antigo)
                nome_arquivo = f"{uuid.uuid4().hex}_{secure_filename(nova_imagem.filename)}"
                nova_imagem.save(os.path.join(UPLOAD_FOLDER, nome_arquivo))
                produto.imagem = nome_arquivo
            else:
                flash('Formato de imagem não permitido.', 'erro')
                return redirect(request.url)

        db.session.commit()
        flash('Produto atualizado com sucesso!', 'sucesso')
        return redirect(url_for('main.list_produtos'))

    return render_template('editar_produto.html', produto=produto, mostrar_apenas_sair=True)

@main.route('/historico')
@login_required
def historico():
    usuario = Usuario.query.get_or_404(session['usuario_id'])
    historico = Historico.query.filter_by(id_usuario=usuario.id).order_by(Historico.data_hora.desc()).all()

    return render_template('historico.html', usuario=usuario, historico=historico, mostrar_apenas_sair=True)

@main.route('/produtos')
@login_required
def list_produtos():
    produtos = Produto.query.options(joinedload(Produto.usuario)).all()
    return render_template('list_produtos.html', produtos=produtos, ocultar_botoes_topo=True, mostrar_botoes_direita=False, mostrar_apenas_sair=True, ocultar_botao_produtos=True, logo_centralizado=True)

@main.route('/perfil')
@login_required
def meu_perfil():
    usuario = Usuario.query.get_or_404(session['usuario_id'])
    total_produtos = Produto.query.filter_by(id_usuario=usuario.id).count()
    return render_template('perfil.html', usuario=usuario, total_produtos=total_produtos, mostrar_apenas_sair=True)

@main.route('/produto/<int:id>/deletar', methods=['POST'])
@login_required
def deletar_produto(id):
    produto = Produto.query.get_or_404(id)
    if produto.id_usuario != session.get('usuario_id'):
        flash('Você não tem permissão para deletar este produto.')
        return redirect(url_for('main.list_produtos'))

    if produto.imagem:
        caminho = os.path.join(UPLOAD_FOLDER, produto.imagem)
        if os.path.exists(caminho):
            os.remove(caminho)

    db.session.delete(produto)
    db.session.commit()
    registrar_acao(session['usuario_id'], 'Produto deletado', produto.nome)
    flash('Produto deletado com sucesso.')
    return redirect(url_for('main.list_produtos'))

@main.route('/produto/<int:id>/chat', methods=['GET', 'POST'])
@login_required
def chat_produto(id):
    produto = Produto.query.options(joinedload(Produto.usuario)).get_or_404(id)
    
    # Corrigido: campo correto é id_produto
    mensagens = Mensagem.query.filter_by(id_produto=id).order_by(Mensagem.data_envio.asc()).all()
    
    usuario_logado = Usuario.query.get_or_404(session.get('usuario_id'))

    if request.method == 'POST':
        conteudo = request.form.get("mensagem", "").strip()
        if conteudo:
            nova_mensagem = Mensagem(
                conteudo=conteudo,
                id_usuario=usuario_logado.id,  # Corrigido: id_usuario
                id_produto=produto.id,         # Corrigido: id_produto
                data_envio=datetime.utcnow()
            )
            db.session.add(nova_mensagem)
            db.session.commit()
            return redirect(url_for('main.chat_produto', id=id))
        else:
            flash("Digite uma mensagem válida.")

    if request.args.get('ajax'):
        return render_template('partials/mensagens.html', mensagens=mensagens, usuario_logado=usuario_logado)

    return render_template('chat_produto.html', produto=produto, mensagens=mensagens, usuario_logado=usuario_logado, mostrar_apenas_sair=True)

@main.route('/produto/<int:id>/detalhes')
@login_required
def detalhes_produto(id):
    produto = Produto.query.options(joinedload(Produto.usuario)).get_or_404(id)
    return render_template('detalhes_produto.html', produto=produto, mostrar_apenas_sair=True)

@main.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    usuario = Usuario.query.get_or_404(session['usuario_id'])

    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        usuario.telefone = request.form.get('telefone')

        nova_foto = request.files.get('foto')
        if nova_foto and nova_foto.filename:
            if extensao_permitida(nova_foto.filename):
                if usuario.foto:
                    caminho_antigo = os.path.join(UPLOAD_FOLDER, usuario.foto)
                    if os.path.exists(caminho_antigo):
                        os.remove(caminho_antigo)
                nome_arquivo = f"{uuid.uuid4().hex}_{secure_filename(nova_foto.filename)}"
                nova_foto.save(os.path.join(UPLOAD_FOLDER, nome_arquivo))
                usuario.foto = nome_arquivo
            else:
                flash('Formato de imagem inválido.', 'erro')
                return redirect(request.url)

        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'sucesso')
        return redirect(url_for('main.meu_perfil'))

    return render_template('editar_perfil.html', usuario=usuario, mostrar_apenas_sair=True)

@main.route('/trocas-doacoes')
@login_required
def trocas_doacoes():
    produtos = Produto.query.filter_by(disponivel=True).all()
    usuarios = Usuario.query.all()
    usuario_logado = Usuario.query.get_or_404(session.get('usuario_id'))
    return render_template(
        'trocas_doacoes.html',
        produtos=produtos,
        usuarios=usuarios,
        usuario_logado=usuario_logado,
        mostrar_apenas_sair=True,
        ocultar_botao_produtos=True,
        ocultar_inicio=False
    )



@main.route('/produto/<int:id>/doar', methods=['POST'])
@login_required
def doar_produto(id):
    produto = Produto.query.get_or_404(id)

    if produto.id_usuario != session.get('usuario_id'):
        flash("Você não tem permissão para doar este produto.", "erro")
        return redirect(url_for('main.trocas_doacoes'))

    nome_destino = request.form.get("usuario_nome")

    if not nome_destino:
        flash("É necessário informar o nome do usuário.", "erro")
        return redirect(url_for('main.trocas_doacoes'))

    # Ignorar espaços e buscar nome insensível a maiúsculas/minúsculas
    usuario_destino = Usuario.query.filter(
        db.func.lower(Usuario.nome) == nome_destino.strip().lower()
    ).first()

    if not usuario_destino:
        flash("Usuário de destino não encontrado.", "erro")
        return redirect(url_for('main.trocas_doacoes'))

    if usuario_destino.id == produto.id_usuario:
        flash("Você não pode doar para si mesmo.", "erro")
        return redirect(url_for('main.trocas_doacoes'))

    produto.id_usuario = usuario_destino.id
    produto.disponivel = False
    db.session.commit()

    registrar_acao(
        id_usuario=session['usuario_id'],
        acao="Produto doado",
        produto=produto.nome,
        destinatario=usuario_destino.nome
    )

    flash(f"Produto doado para {usuario_destino.nome} com sucesso!", "sucesso")
    return redirect(url_for('main.trocas_doacoes'))

@main.route('/produto/<int:id>/contato')
@login_required
def contato_produto(id):
    produto = Produto.query.get_or_404(id)
    return render_template('contato_produto.html', produto=produto, mostrar_apenas_sair=True)
