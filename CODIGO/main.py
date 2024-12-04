import sqlite3
import os
from fasthtml.common import fast_app, serve, Form, Input, Button, Div, Redirect
from passlib.hash import bcrypt

app, routes = fast_app()

DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "DATABASE.db")

def inicializar_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''CREATE TABLE usuarios (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                usuario TEXT NOT NULL,
                                senha TEXT NOT NULL
                            )''')

inicializar_db()

def executar_db(query, parametros=(), fetchone=False):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, parametros)
        conn.commit()
        return cursor.fetchone() if fetchone else cursor.fetchall()

def criptografar_senha(senha):
    return bcrypt.hash(senha)

def verificar_senha(senha, hash_armazenado):
    return bcrypt.verify(senha, hash_armazenado)

@routes("/", methods=["GET"])
def index(request):
    return Div(
        Div("😃Seja Bem-vindo a um exemplo Básico de Formulário de Cadastro e Login com FastHTML! Escolha uma opção: 👇", class_="welcome-message", style="margin: 40px; text-align: center; font-size: 40px"),
        Div(
            Button("CADASTRAR", onclick="window.location='/register'", class_="btn-register", style="margin-right: 10px; padding: 10px 20px;"),
            Button("LOGIN", onclick="window.location='/login'", class_="btn-login", style="padding: 10px 20px;"),
            style="display: flex; justify-content: center;"
        ),
        style="text-align: center; margin-top: 50px;"
    )

@routes("/login", methods=["GET", "POST"])
async def login(request):
    if request.method == "POST":
        form_data = await request.form()
        usuario, senha = form_data.get("usuario"), form_data.get("senha")
        
        if not usuario or not senha:
            return exibir_mensagem("😡Por favor, preencha ambos os campos!", erro=True)
        
        resultado = executar_db("SELECT senha FROM usuarios WHERE usuario = ?", (usuario,), fetchone=True)
        
        if not resultado:
            return exibir_mensagem("🤬Usuário não encontrado. Tente novamente!", erro=True)
        
        if verificar_senha(senha, resultado[0]):
            return Redirect("/tasks")
        return exibir_mensagem("🤬Senha incorreta. Tente novamente!", erro=True)
    
    return renderizar_formulario("/login", "LOGIN")

@routes("/register", methods=["GET", "POST"])
async def register(request):
    if request.method == "POST":
        form_data = await request.form()
        usuario, senha = form_data.get("usuario"), form_data.get("senha")

        if not usuario or not senha:
            return exibir_mensagem("😡Por favor, preencha ambos os campos!", erro=True)

        if executar_db("SELECT 1 FROM usuarios WHERE usuario = ?", (usuario,), fetchone=True):
            return exibir_mensagem("🤨Este usuário já está cadastrado!", erro=True)

        senha_criptografada = criptografar_senha(senha)
        executar_db("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha_criptografada))
        return Redirect("/login")

    return renderizar_formulario("/register", "CADASTRAR")

@routes("/tasks")
def tasks_page(request):
    return Div(
        Div(
            "☺️Bem-vindo à sua página de inicial!",
            class_="task-welcome-message",
            style="text-align: center; font-size: 60px; margin-top: 50px; animation: fadeIn 5s ease-in-out;"
        ),
        class_="task-page"
    )

def renderizar_formulario(action, botao_texto):
    return Div(
        Form(
            Div(
                Input(type="text", name="usuario", placeholder="Nome de usuário", required=True, style="margin-bottom: 15px; padding: 10px; width: 100%;"),
                Input(type="password", name="senha", placeholder="Senha", required=True, style="margin-bottom: 15px; padding: 10px; width: 100%;"),
                style="margin-bottom: 20px;"
            ),
            Button(botao_texto, type="submit", style="padding: 10px 20px;"),
            action=action, method="post", style="max-width: 300px; margin: auto; display: block;"
        ),
        style="text-align: center; margin-top: 50px;"
    )

def exibir_mensagem(mensagem, erro=False):
    cor = "red" if erro else "green"
    return Div(mensagem, class_="message", style=f"color: {cor}; margin: 20px; text-align: center; font-size: 40px; animation: fadeIn 2s ease-in-out;")

serve()
