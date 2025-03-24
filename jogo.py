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
    
    x_personagem = 50
    y_personagem = ALTURA // 2
    
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
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    if resposta_usuario == resposta_correta:
                        x_personagem += 50  # Move para a direita
                        pontuacao += 1
                    resposta_usuario = ""
                    pergunta, resposta_correta = gerar_pergunta(dificuldade)
                elif evento.key == pygame.K_BACKSPACE:
                    resposta_usuario = resposta_usuario[:-1]
                else:
                    resposta_usuario += evento.unicode
    
    salvar_recorde(nome, pontuacao, dificuldade)

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

def criar_tabelas():
    try:
        # Conecta ao banco de dados
        with sqlite3.connect('recordes.db') as conn:
            cursor = conn.cursor()

            # Criação da tabela de usuários (se não existir)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL
                )
            ''')

            # Criação da tabela de progresso (se não existir)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progresso (
                    id_progresso INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_usuario INTEGER,
                    pontuacao INTEGER NOT NULL,
                    dificuldade TEXT NOT NULL,
                    fase INTEGER NOT NULL,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
                )
            ''')

            print("Tabelas criadas com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro ao criar as tabelas: {e}")


def registrar_usuario(nome, senha):
    try:
        # Conecta ao banco de dados
        with sqlite3.connect('recordes.db') as conn:
            cursor = conn.cursor()

            # Verifica se o usuário já existe
            cursor.execute('''
                SELECT id_usuario FROM usuarios WHERE nome = ?
            ''', (nome,))
            resultado = cursor.fetchone()

            if resultado:
                print("Usuário já existe!")
                return resultado[0]  # Retorna o id_usuario se já existir
            else:
                # Insere um novo usuário
                cursor.execute('''
                    INSERT INTO usuarios (nome, senha)
                    VALUES (?, ?)
                ''', (nome, senha))
                conn.commit()

                # Retorna o id do novo usuário
                cursor.execute('''
                    SELECT id_usuario FROM usuarios WHERE nome = ?
                ''', (nome,))
                id_usuario = cursor.fetchone()[0]
                print(f"Novo usuário {nome} registrado com ID {id_usuario}")
                return id_usuario

    except sqlite3.Error as e:
        print(f"Erro ao registrar o usuário: {e}")
        return None

def salvar_progresso(id_usuario, pontuacao, dificuldade, fase):
    try:
        # Conecta ao banco de dados
        with sqlite3.connect('recordes.db') as conn:
            cursor = conn.cursor()

            # Insere o progresso do usuário na tabela de progresso
            cursor.execute('''
                INSERT INTO progresso (id_usuario, pontuacao, dificuldade, fase)
                VALUES (?, ?, ?, ?)
            ''', (id_usuario, pontuacao, dificuldade, fase))

            conn.commit()
            print(f"Progresso de ID {id_usuario} salvo com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro ao salvar o progresso: {e}")


if __name__ == "__main__":
    nome, senha, dificuldade = tela_inicial()
    jogo(nome, dificuldade)
    pygame.quit()