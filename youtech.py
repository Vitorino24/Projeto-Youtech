from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
import uuid

app = Flask(__name__)
app.secret_key = "youtech"
usuario = "usuario"
senha = "senha" 
login = False

#FUNCAO PARA VERIFICAR SESSÃO
def verifica_sessao():
    if "login" in session and session["login"]:
        return True
    else:
        return False

# CONEXÃO COM O BANCO DE DADOS
def conecta_database():
    conexao = sql.connect("db_youtech.db")
    conexao.row_factory = sql.Row
    return conexao

#INICIAR O BANCO DE DADOS
def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit()
    conexao.close()

# ROTA DA PÁGINA INICIAL
@app.route("/")
def index():
    title = "Home"
    return render_template("home.html", title=title)
   

@app.route("/vagas")
def vagas():
    iniciar_db()
    conexao = conecta_database()
    vagas = conexao.execute('SELECT * FROM vagas ORDER BY id_vaga DESC').fetchall()
    conexao.close()
    title = "Vagas"
    return render_template("vagas.html", vagas=vagas, title=title)
    

@app.route("/infovaga/<id>")
def infovaga(id):
    conexao = conecta_database()
    vagas = conexao.execute('SELECT * FROM vagas WHERE id_vaga = ?', (id,)).fetchall()
    conexao.close()
    title = "Informação de vagas"
    return render_template("infovaga.html", vagas=vagas, title=title)
    




#ROTA DA PÁGINA DE ADM
@app.route("/adm")
def adm():
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        vagas = conexao.execute('SELECT * FROM vagas ORDER BY id_vaga DESC').fetchall()
        conexao.close()
        title = "Administração"
        return render_template("adm.html", vagas=vagas, title=title)
    else:
        return redirect("/login")
    
# ROTA DA PÁGINA ACESSO
@app.route("/acesso", methods=['post'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if usuario == usuario_informado and senha == senha_informada:
        session["login"] = True
        return redirect('/adm')
    else:
        return render_template("login.html",msg="Usuário/Senha estão incorretos!")
    
#ROTA DA PÁGINA LOGIN
@app.route("/login")
def login():
    title="Login"
    return render_template("login.html", title=title)

#ROTA DA PÁGINA GRUPO YOUTECH
@app.route("/grupoyoutech")
def grupoyoutech():
    title="grupo youtech"
    return render_template("grupoyoutech.html", title=title)

#ROTA DA PÁGINA DE CADASTRO
@app.route("/cadvagas")
def cadvagas():
    if verifica_sessao():
        title = "Cadastro de Vagas"
        return render_template("cadvagas.html", title=title)
    else:
        return redirect("/login")
    

#ROTA DA PÁGINA DE CADASTRO NO BANCO
@app.route("/cadastrar", methods=["post"])
def cadastrar():
    if verifica_sessao():
        cargo_vaga=request.form['cargo_vaga']
        requisitos_vaga=request.form['requisitos_vaga']
        salario_vaga=request.form['salario_vaga']
        local_vaga=request.form['local_vaga']
        tipo_vaga=request.form['tipo_vaga']
        email_vaga=request.form['email_vaga']
        img_vaga=request.files['img_vaga']
        id_foto=str(uuid.uuid4().hex)
        filename=id_foto+cargo_vaga+'.png'
        img_vaga.save("static/img/vagas/"+filename)
        conexao = conecta_database()
        conexao.execute('INSERT INTO vagas (cargo_vaga, requisitos_vaga, salario_vaga, local_vaga, tipo_vaga, email_vaga, img_vaga) VALUES (?, ?, ?, ?, ?, ?, ?)', (cargo_vaga, requisitos_vaga, salario_vaga, local_vaga, tipo_vaga, email_vaga, filename))
        conexao.commit()
        conexao.close()
        return redirect("/adm")
    else:  
        return redirect("/login")
    
#CÓDIGO DO LOGOUT
@app.route("/logout")
def logout():
    global login
    login = False
    session.clear()
    return redirect('/')

@app.route("/excluir/<id>")
def excluir(id):
    if verifica_sessao():
        id = int(id)
        conexao = conecta_database()
        conexao.execute('DELETE FROM vagas WHERE id_vaga = ?', (id,))
        conexao.commit()
        conexao.close()
        return redirect('/adm')
    else:
        return redirect("/login")
    

#CRIAR A ROTA DO EDITAR
@app.route("/editvagas/<id_vaga>")
def editar(id_vaga):
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        vagas = conexao.execute('SELECT * FROM vagas WHERE id_vaga = ?', (id_vaga,)).fetchall()
        conexao.close()
        title = "Edição de vagas"
        return render_template("editvagas.html", vagas=vagas, title=title)
    else:
        return redirect("/login")
    
@app.route("/editarvagas", methods=['POST'])
def editvagas():
    id_vaga = request.form['id_vaga']
    cargo_vaga = request.form['cargo_vaga']
    requisitos_vaga = request.form['requisitos_vaga']
    salario_vaga = request.form['salario_vaga']
    local_vaga = request.form['local_vaga']
    tipo_vaga = request.form['tipo_vaga']
    email_vaga = request.form['email_vaga']
    img_vaga = request.files['img_vaga']
    nomeimg_vaga = request.form['nomeimg_vaga']

    conexao = conecta_database()
    conexao.execute('UPDATE vagas SET cargo_vaga = ?, requisitos_vaga = ?, salario_vaga = ?, local_vaga = ?, tipo_vaga = ?, email_vaga = ? WHERE id_vaga = ?', (cargo_vaga, requisitos_vaga, salario_vaga, local_vaga, tipo_vaga, email_vaga, id_vaga))
    conexao.commit()
    conexao.close()

    if img_vaga:
        img_vaga.save("static/img/vagas/"+ nomeimg_vaga)
    
    return redirect('/adm')


#ROTA da pág de busca
@app.route("/busca",methods=["post"])
def busca():
    busca=request.form['buscar']
    conexao = conecta_database()
    vagas = conexao.execute('SELECT * FROM vagas WHERE cargo_vaga LIKE "%" || ? || "%"',(busca,)).fetchall()
    title = "Busca"
    return render_template("vagas.html", vagas=vagas, title=title)



# FINAL DO CODIGO - EXECUTANDO O SERVIDOR
app.run(debug=True)