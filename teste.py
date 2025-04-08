import pygame
import random
import sqlite3
from datetime import datetime

# Inicializa o Pygame
pygame.init()

# Configurações da tela
LARGURA, ALTURA = 800, 400
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo de Matemática")

# Fonte
fonte = pygame.font.Font(None, 36)

# Carregar imagens
fundo = pygame.image.load("fundoGamePy.jpg")
fundo = pygame.transform.scale(fundo, (LARGURA, ALTURA))
fundo_inicial = pygame.image.load("tela_inicial.png")
fundo_inicial = pygame.transform.scale(fundo_inicial, (LARGURA, ALTURA))
personagem = pygame.image.load("personagem.png")
personagem = pygame.transform.scale(personagem, (60, 60))
inimigo = pygame.image.load("inimigo.png")
inimigo = pygame.transform.scale(inimigo, (50, 50))

# Banco de dados

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
                data TEXT NOT NULL,
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
                return resultado[0]
            else:
                print("Senha incorreta!")
                return None
        cursor.execute("INSERT INTO usuarios (nome, senha) VALUES (?, ?)", (nome, senha))
        conn.commit()
        return cursor.lastrowid


def salvar_recorde(id_usuario, pontuacao, dificuldade):
    with sqlite3.connect('recordes.db') as conn:
        cursor = conn.cursor()
        data_atual = datetime.now().strftime('%Y-%m')
        cursor.execute("INSERT INTO recordes (id_usuario, dificuldade, pontuacao, data) VALUES (?, ?, ?, ?)",
                       (id_usuario, dificuldade, pontuacao, data_atual))
        conn.commit()


def obter_recordes(id_usuario, dificuldade):
    with sqlite3.connect('recordes.db') as conn:
        cursor = conn.cursor()

        # Recorde pessoal
        cursor.execute("SELECT MAX(pontuacao) FROM recordes WHERE id_usuario = ?", (id_usuario,))
        recorde_pessoal = cursor.fetchone()[0] or 0

        # Recorde do mês
        data_atual = datetime.now().strftime('%Y-%m')
        cursor.execute("SELECT MAX(pontuacao) FROM recordes WHERE data = ?", (data_atual,))
        recorde_mes = cursor.fetchone()[0] or 0

        # Recorde geral
        cursor.execute("SELECT MAX(pontuacao) FROM recordes")
        recorde_geral = cursor.fetchone()[0] or 0

        # Recorde por dificuldade
        cursor.execute("SELECT MAX(pontuacao) FROM recordes WHERE dificuldade = ?", (dificuldade,))
        recorde_dificuldade = cursor.fetchone()[0] or 0

        return recorde_pessoal, recorde_mes, recorde_geral, recorde_dificuldade


def tela_final(id_usuario, dificuldade, pontuacao):
    salvar_recorde(id_usuario, pontuacao, dificuldade)
    recorde_pessoal, recorde_mes, recorde_geral, recorde_dificuldade = obter_recordes(id_usuario, dificuldade)

    rodando = True
    while rodando:
        TELA.fill((30, 30, 30))
        TELA.blit(fonte.render(f"Pontuação Final: {pontuacao}", True, (255, 255, 255)), (50, 50))
        TELA.blit(fonte.render(f"Recorde Pessoal: {recorde_pessoal}", True, (0, 255, 0)), (50, 100))
        TELA.blit(fonte.render(f"Recorde do Mês: {recorde_mes}", True, (0, 255, 255)), (50, 150))
        TELA.blit(fonte.render(f"Recorde Geral: {recorde_geral}", True, (255, 255, 0)), (50, 200))
        TELA.blit(fonte.render(f"Recorde na Dificuldade: {recorde_dificuldade}", True, (255, 100, 255)), (50, 250))
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False


def gerar_pergunta(dificuldade):
    if dificuldade == "facil":
        a, b = random.randint(1, 10), random.randint(1, 10)
    elif dificuldade == "medio":
        a, b = random.randint(10, 50), random.randint(10, 50)
    else:
        a, b = random.randint(50, 100), random.randint(50, 100)

    operador = random.choice(["+", "-", "*"])
    pergunta = f"{a} {operador} {b}"
    resposta_correta = str(eval(pergunta))
    return f"Quanto é {pergunta}?", resposta_correta


def tela_inicial():
    nome = ""
    senha = ""
    dificuldade = "facil"
    ativo = "nome"
    rodando = True

    while rodando:
        TELA.blit(fundo_inicial, (0, 0))
        TELA.blit(fonte.render("Digite seu Nome, Senha e Escolha a Dificuldade", True, (0, 0, 0)), (100, 30))
        TELA.blit(fonte.render(f"Nome: {nome}", True, (0, 0, 0)), (250, 80))
        TELA.blit(fonte.render(f"Senha: {'*'*len(senha)}", True, (0, 0, 0)), (250, 120))
        TELA.blit(fonte.render(f"Dificuldade: {dificuldade}", True, (0, 0, 0)), (250, 160))
        TELA.blit(fonte.render("TAB para mudar campo e Pressione ENTER para iniciar:", True, (0, 0, 0)), (80, 300))
        TELA.blit(fonte.render("Pressione 1,2,3 para mudar a dificuldade", True, (0, 0, 0)), (80, 330))

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
                elif evento.key == pygame.K_TAB:
                    if ativo == "nome": ativo = "senha"
                    elif ativo == "senha": ativo = "dificuldade"
                    else: ativo = "nome"
                elif evento.key == pygame.K_BACKSPACE:
                    if ativo == "nome": nome = nome[:-1]
                    elif ativo == "senha": senha = senha[:-1]
                elif evento.key in [pygame.K_1, pygame.K_2, pygame.K_3] and ativo == "dificuldade":
                    dificuldade = "facil" if evento.key == pygame.K_1 else "medio" if evento.key == pygame.K_2 else "dificil"
                else:
                    if ativo == "nome": nome += evento.unicode
                    elif ativo == "senha": senha += evento.unicode


def jogo(id_usuario, dificuldade):
    x_personagem = 50
    y_personagem = ALTURA - 80  # Mais perto do "chão"

    x_inimigo = 630
    y_inimigo = ALTURA - 80
    
    resposta_usuario = ""
    vidas = 3
    pontuacao = 0
    pergunta, resposta_correta = gerar_pergunta(dificuldade)
    velocidade = 5

    rodando = True
    while rodando:
        TELA.blit(fundo, (0, 0))
        TELA.blit(fonte.render(pergunta, True, (0, 0, 0)), (50, 20))
        TELA.blit(fonte.render(resposta_usuario, True, (0, 0, 255)), (50, 60))
        TELA.blit(personagem, (x_personagem, y_personagem))
        TELA.blit(inimigo, (x_inimigo, y_inimigo))
        
        for i in range(vidas):
            pygame.draw.circle(TELA, (255, 0, 0), (LARGURA - (i + 1) * 40, 30), 15) # Exibir barra de vida
 
        if x_personagem < x_inimigo + 50 and x_personagem + 50 > x_inimigo and y_personagem < y_inimigo + 50 and y_personagem + 50 > y_inimigo: # Verificar se o inimigo alcançou com o personagem
            vidas -= 1
            x_inimigo = 630  # Voltar o inimigo para a posição inicial após acertar o personagem
            if vidas <= 0:
                rodando = False  # Volta pra tela inicial quando o personagem perde as 3 vidas
                break

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    if resposta_usuario == resposta_correta:
                        x_personagem += velocidade
                        pontuacao += 1
                    else:
                        x_inimigo += -50 # Move para a esquerda
                    resposta_usuario = ""
                    pergunta, resposta_correta = gerar_pergunta(dificuldade)
                elif evento.key == pygame.K_BACKSPACE:
                    resposta_usuario = resposta_usuario[:-1]
                else:
                    resposta_usuario += evento.unicode

    tela_final(id_usuario, dificuldade, pontuacao)


if __name__ == "__main__":
    criar_tabelas()
    id_usuario, dificuldade = tela_inicial()
    jogo(id_usuario, dificuldade)
    pygame.quit()
