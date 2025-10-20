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