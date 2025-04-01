import pygame
import random
import pandas as pd
import sqlite3

'''''
Interface gráfica e Mecânica do Jogo (Pygame) → Responsável por exibir o jogo, movimentação do personagem e do inimigo.
Gerador de Perguntas e Respostas → Criar lógica para gerar contas matemáticas conforme a dificuldade.
Sistema de Fases (Fácil, Médio, Difícil) → Implementar níveis de dificuldade, ajustando tempo e complexidade.
Lógica do Inimigo ("Bixo") → Criar um sistema onde o inimigo persegue o jogador conforme o tempo passa.
Sistema de Configuração (Escolha de número de contas e tempo) → Criar menu onde o usuário escolhe a dificuldade e número de perguntas.
Sistema de Registro de Pontuação (Excel ou JSON) → Salvar recordes e progresso para estimular aprendizado.
'''

''''
#Fazer um jogo de matemática.
#Dividir o jogo em 3 fases - fácil, médio e dificil.
#Fazer primeiramente a fase fácil, depois replicar o código aumentando o nível das contas e diminuindo o tempo.
#A lógica do jogo resume em o usuário acertar a conta e ir andando, fugindo de um "bixo" que anda atrelado ao tempo.
#O usuário pode escolher o número de contas que terá para desenvolver em X tempo (pode ser 60 segundos)
#Desenvolver a lógica de contas matemáticas com base no numero de contas que o usuário escolher/
#inicialmente salvar em um excel os dados e salvar como "record", para estimular o ensino.
'''


# Inicializa o Pygame
pygame.init()

# Configurações da tela
LARGURA, ALTURA = 800, 400
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo de Matemática")

# Fonte
fonte = pygame.font.Font(None, 36)

def criar_tabelas():
    with sqlite3.connect('recordes.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recordes (
                id_recorde INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                dificuldade TEXT NOT NULL,
                pontuacao INTEGER NOT NULL,
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
            )
        ''')

def registrar_usuario(nome, senha):
    with sqlite3.connect('recordes.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, senha FROM usuarios WHERE nome = ?", (nome,))
        resultado = cursor.fetchone()
        if resultado:
            if resultado[1] == senha:
                return resultado[0]  # Usuário já registrado, retorna ID
            else:
                print("Senha incorreta!")
                return None
        cursor.execute("INSERT INTO usuarios (nome, senha) VALUES (?, ?)", (nome, senha))
        conn.commit()
        return cursor.lastrowid

def salvar_recorde(id_usuario, pontuacao, dificuldade):
    with sqlite3.connect('recordes.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT pontuacao FROM recordes WHERE id_usuario = ? AND dificuldade = ?", (id_usuario, dificuldade))
        recorde_atual = cursor.fetchone()
        if recorde_atual:
            if pontuacao > recorde_atual[0]:
                cursor.execute("UPDATE recordes SET pontuacao = ? WHERE id_usuario = ? AND dificuldade = ?", (pontuacao, id_usuario, dificuldade))
        else:
            cursor.execute("INSERT INTO recordes (id_usuario, dificuldade, pontuacao) VALUES (?, ?, ?)", (id_usuario, dificuldade, pontuacao))
        conn.commit()

def tela_inicial():
    nome = ""
    senha = ""
    dificuldade = "facil"
    ativo = "nome"
    rodando = True
    
    while rodando:
        TELA.fill((200, 200, 200))  # Fundo cinza
        
        texto_titulo = fonte.render("Digite seu Nome, Senha e Escolha a Dificuldade", True, (0, 0, 0))
        TELA.blit(texto_titulo, (150, 50))
        
        texto_nome = fonte.render(f"Nome: {nome}", True, (0, 0, 0))
        TELA.blit(texto_nome, (250, 100))
        
        texto_senha = fonte.render(f"Senha: {'*' * len(senha)}", True, (0, 0, 0))
        TELA.blit(texto_senha, (250, 150))
        
        texto_dificuldade = fonte.render(f"Dificuldade: {dificuldade}", True, (0, 0, 0))
        TELA.blit(texto_dificuldade, (250, 200))
        
        texto_instrucao = fonte.render("Pressione ENTER para continuar", True, (0, 0, 0))
        TELA.blit(texto_instrucao, (250, 250))
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    id_usuario = registrar_usuario(nome, senha)
                    if id_usuario:
                        return id_usuario, dificuldade
                    rodando = False
                elif evento.key == pygame.K_TAB:
                    if ativo == "nome":
                        ativo = "senha"
                    elif ativo == "senha":
                        ativo = "dificuldade"
                    else:
                        ativo = "nome"
                elif evento.key == pygame.K_BACKSPACE:
                    if ativo == "nome":
                        nome = nome[:-1]
                    elif ativo == "senha":
                        senha = senha[:-1]
                elif evento.key in [pygame.K_1, pygame.K_2, pygame.K_3] and ativo == "dificuldade":
                    dificuldade = "facil" if evento.key == pygame.K_1 else "medio" if evento.key == pygame.K_2 else "dificil"
                else:
                    if ativo == "nome":
                        nome += evento.unicode
                    elif ativo == "senha":
                        senha += evento.unicode
    
    return nome, senha, dificuldade

def jogo(nome, dificuldade):
    personagem = pygame.image.load("personagem.png")
    personagem = pygame.transform.scale(personagem, (50, 50))

    inimigo = pygame.image.load("inimigo.png")
    inimigo = pygame.transform.scale(inimigo, (50, 50))
    
    x_personagem = 50
    y_personagem = ALTURA // 2

    x_inimigo = 630
    y_inimigo = ALTURA // 2
    
    vidas = 3
    pergunta, resposta_correta = gerar_pergunta(dificuldade)
    resposta_usuario = ""
    pontuacao = 0
    rodando = True
    
    while rodando:
        TELA.fill((255, 255, 255))  # Fundo branco
        
        texto = fonte.render(pergunta, True, (0, 0, 0))
        TELA.blit(texto, (50, 50))
        
        resposta_texto = fonte.render(resposta_usuario, True, (0, 0, 255))
        TELA.blit(resposta_texto, (50, 100))
        
        TELA.blit(personagem, (x_personagem, y_personagem))

        TELA.blit(inimigo, (x_inimigo, y_inimigo))
        
        for i in range(vidas):
            pygame.draw.circle(TELA, (255, 0, 0), (LARGURA - (i + 1) * 40, 30), 15) # Exibir barra de vida

        if x_personagem < x_inimigo + 50 and x_personagem + 50 > x_inimigo and y_personagem < y_inimigo + 50 and y_personagem + 50 > y_inimigo: # Verificar se o inimigo alcançou com o personagem
            vidas -= 1
            x_inimigo = 630  # Voltar o inimigo para a posição inicial após acertar o personagem
            if vidas <= 0:
                tela_inicial()  # Volta pra tela inicial quando o personagem perde as 3 vidas


        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    if resposta_usuario == resposta_correta:
                        x_personagem += 50  # Move para a direita
                        pontuacao += 1
                    else:
                        x_inimigo += -50 # Move para a esquerda
                    resposta_usuario = ""
                    pergunta, resposta_correta = gerar_pergunta(dificuldade)
                elif evento.key == pygame.K_BACKSPACE:
                    resposta_usuario = resposta_usuario[:-1]
                else:
                    resposta_usuario += evento.unicode
    
    salvar_recorde(id_usuario, pontuacao, dificuldade)

def gerar_pergunta(dificuldade):
    if dificuldade == "facil":
        a, b = random.randint(1, 10), random.randint(1, 10)
    elif dificuldade == "medio":
        a, b = random.randint(10, 50), random.randint(10, 50)
    else:
        a, b = random.randint(50, 100), random.randint(50, 100)
    
    operador = random.choice(["+", "-", "*"])
    pergunta = f"Quanto é {a} {operador} {b}?"
    resposta_correta = str(eval(f"{a}{operador}{b}"))
    return pergunta, resposta_correta

if __name__ == "__main__":
    criar_tabelas()
    id_usuario, dificuldade = tela_inicial()
    jogo(id_usuario, dificuldade)
    pygame.quit()
