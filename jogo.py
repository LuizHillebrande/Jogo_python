import pygame
import random
import pandas as pd

'''
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

# Carrega a imagem do personagem
personagem = pygame.image.load("personagem.png")
personagem = pygame.transform.scale(personagem, (50, 50))

# Posição inicial do personagem
x_personagem = 50
y_personagem = ALTURA // 2

# Fonte
fonte = pygame.font.Font(None, 36)

# Configurações do jogo
dificuldade = "facil"  # Pode ser "facil", "medio" ou "dificil"
num_perguntas = 5  # Número de perguntas no jogo
tempo_limite = 60  # Tempo total do jogo em segundos

# Função para gerar perguntas matemáticas
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

# Função para registrar recordes
def salvar_recorde(nome, pontuacao):
    df = pd.DataFrame({"Nome": [nome], "Pontuação": [pontuacao]})
    try:
        df_existente = pd.read_excel("recordes.xlsx")
        df = pd.concat([df_existente, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_excel("recordes.xlsx", index=False)

# Inicializa primeira pergunta
pergunta, resposta_correta = gerar_pergunta(dificuldade)
resposta_usuario = ""
pontuacao = 0

# Loop principal
tempo_rodando = True
while tempo_rodando:
    TELA.fill((255, 255, 255))  # Fundo branco
    
    # Exibe a pergunta
    texto = fonte.render(pergunta, True, (0, 0, 0))
    TELA.blit(texto, (50, 50))
    
    # Exibe a resposta digitada
    resposta_texto = fonte.render(resposta_usuario, True, (0, 0, 255))
    TELA.blit(resposta_texto, (50, 100))
    
    # Exibe o personagem
    TELA.blit(personagem, (x_personagem, y_personagem))
    
    pygame.display.flip()
    
    # Captura eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            tempo_rodando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                if resposta_usuario == resposta_correta:
                    x_personagem += 50  # Move para a direita 50 px
                    pontuacao += 1
                resposta_usuario = ""  # Reseta a resposta
                pergunta, resposta_correta = gerar_pergunta(dificuldade)
            elif evento.key == pygame.K_BACKSPACE:
                resposta_usuario = resposta_usuario[:-1]
            else:
                resposta_usuario += evento.unicode  # Adiciona a tecla pressionada

# Salva pontuação ao final
tempo_rodando = False
nome_jogador = input("Digite seu nome para salvar o recorde: ")
salvar_recorde(nome_jogador, pontuacao)
pygame.quit()
