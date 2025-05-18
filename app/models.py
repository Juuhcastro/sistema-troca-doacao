from app import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    endereco = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    foto = db.Column(db.String(100), nullable=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    produtos = db.relationship('Produto', backref='usuario', lazy=True)
    mensagens_enviadas = db.relationship('Mensagem', backref='autor', lazy=True)


class Produto(db.Model):
    __tablename__ = 'produto'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    categoria = db.Column(db.String(50))
    tipo = db.Column(db.String(20))
    condicao = db.Column(db.String(50))
    imagem = db.Column(db.String(100), nullable=True)

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    localizacao = db.Column(db.String(100))
    data_cadastro = db.Column(db.Date, default=datetime.utcnow)
    estado_conservacao = db.Column(db.Text)

    altura = db.Column(db.String(10))
    largura = db.Column(db.String(10))
    profundidade = db.Column(db.String(10))

    voltagem = db.Column(db.String(10))
    nivel_ruido = db.Column(db.String(50))
    sistema = db.Column(db.String(100))
    observacoes = db.Column(db.Text)

    disponivel = db.Column(db.Boolean, default=True)

    # Relacionamento com mensagens
    mensagens = db.relationship('Mensagem', backref='produto', lazy=True)


class Mensagem(db.Model):
    __tablename__ = 'mensagem'

    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)

    id_produto = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    # Nenhum relacionamento adicional aqui – já é resolvido com backref='autor'


class Historico(db.Model):
    __tablename__ = 'historico'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    acao = db.Column(db.String(100), nullable=False)
    produto = db.Column(db.String(100))
    destinatario = db.Column(db.String(100))
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', backref='historicos')
