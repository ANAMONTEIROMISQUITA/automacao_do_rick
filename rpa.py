import requests
import sqlite3
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def coletar_dados_rick():
    url = "https://rickandmortyapi.com/api/character"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        personagens = data['results']  

        conexao = sqlite3.connect("projeto_rpa.db")
        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ricks (
                id INTEGER PRIMARY KEY,
                name TEXT,
                status TEXT,
                species TEXT,
                gender TEXT
            )
        """)

        for personagem in personagens[:10]:
            id_personagem = personagem['id']
            nome = personagem['name']
            status = personagem['status']
            especie = personagem['species']
            genero = personagem['gender']

            cursor.execute("""
                INSERT OR IGNORE INTO ricks (id, name, status, species, gender)
                VALUES (?, ?, ?, ?, ?)
            """, (id_personagem, nome, status, especie, genero))

        conexao.commit()
        conexao.close()
        print("✅ Dados coletados e armazenados com sucesso!")

    else:
        print(f"❌ Erro ao acessar API: {response.status_code}")

def filtrar_dados_processados():
    conexao = sqlite3.connect("projeto_rpa.db")
    cursor = conexao.cursor()

    regex_status = re.compile(r'^Alive$', re.IGNORECASE)
    regex_genero = re.compile(r'^Male$', re.IGNORECASE)

    cursor.execute("SELECT * FROM ricks")
    dados = cursor.fetchall()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dados_processados (
            id INTEGER PRIMARY KEY,
            name TEXT,
            status TEXT,
            species TEXT,
            gender TEXT
        )
    """)

    for dado in dados:
        id_, nome, status, especie, genero = dado

        if regex_status.match(status) and regex_genero.match(genero):
            cursor.execute("""
                INSERT OR IGNORE INTO dados_processados (id, name, status, species, gender)
                VALUES (?, ?, ?, ?, ?)
            """, (id_, nome, status, especie, genero))
            print(f"✅ Salvo em dados_processados: {nome} - {status} - {genero}")

    conexao.commit()
    conexao.close()
    print("✅ Dados filtrados e salvos com sucesso!")

def enviar_email_confirmacao():
    try:
        remetente = "anaclaudia.misquita@gmail.com"
        senha_app = "zyfhqqfasymjdcri"  
        destinatario = "anaclaudia.misquita@gmail.com"

        conexao = sqlite3.connect("projeto_rpa.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM dados_processados")
        dados = cursor.fetchall()
        conexao.close()

        corpo = "Olá,\n\nOs dados do Rick and Morty foram coletados, filtrados e armazenados com sucesso em SQLite.\n\n"
        corpo += "Segue a lista dos personagens filtrados:\n\n"

        if not dados:
            corpo += "Nenhum dado processado encontrado.\n"
        else:
            for linha in dados:
                id_, nome, status, especie, genero = linha
                corpo += f"- {nome} | Status: {status} | Espécie: {especie} | Gênero: {genero}\n"

        corpo += "\nAtenciosamente,\nAutomação da Ana 🤖"

        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = "Confirmação de Processamento - RPA Python"
        msg.attach(MIMEText(corpo, 'plain'))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(remetente, senha_app)
            server.send_message(msg)

        print("E-mail de confirmação enviado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")