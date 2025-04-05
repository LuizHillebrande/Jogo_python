import pygame
import random
import pandas as pd

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
fundo = pygame.image.load("fundoGamePy.jpg")
fundo = pygame.transform.scale(fundo, (LARGURA, ALTURA)) 
pygame.display.set_caption("Jogo de Matemática")

fundo_inicial = pygame.image.load("tela_inicial.png")
fundo_inicial = pygame.transform.scale(fundo_inicial, (LARGURA, ALTURA))

# Fonte
fonte = pygame.font.Font(None, 36)

def tela_inicial():
    nome = ""
    senha = ""
    dificuldade = "facil"
    ativo = "nome"
    rodando = True
    
    while rodando:
        TELA.blit(fundo_inicial, (0, 0))
        
        texto_titulo = fonte.render("Digite seu Nome, Senha e Escolha a Dificuldade", True, (0, 0, 0))
        TELA.blit(texto_titulo, (150, 50))
        
        texto_nome = fonte.render(f"Nome: {nome}", True, (0, 0, 0))
        TELA.blit(texto_nome, (250, 100))
        
        texto_senha = fonte.render(f"Senha: {'*' * len(senha)}", True, (0, 0, 0))
        TELA.blit(texto_senha, (250, 150))
        
        texto_dificuldade = fonte.render(f"Dificuldade: {dificuldade}", True, (0, 0, 0))
        TELA.blit(texto_dificuldade, (250, 200))
        
        texto_instrucao = fonte.render("Pressione ENTER para continuar", True, (0, 0, 0))
        TELA.blit(texto_instrucao, (250, 350))
        
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
    TELA.blit(fundo, (0, 0))
    personagem = pygame.image.load("personagem.png")
    personagem = pygame.transform.scale(personagem, (120, 120))

    x_personagem = 509
    y_personagem = ALTURA // 1.75
    
    pergunta, resposta_correta = gerar_pergunta(dificuldade)
    resposta_usuario = ""
    pontuacao = 0
    rodando = True
    
    while rodando:
        TELA.blit(fundo, (0, 0))  # Primeiro, desenha o fundo
    
        texto = fonte.render(pergunta, True, (0, 0, 0))
        TELA.blit(texto, (50, 50))
        
        resposta_texto = fonte.render(resposta_usuario, True, (0, 0, 255))
        TELA.blit(resposta_texto, (50, 100))
        
        TELA.blit(personagem, (x_personagem, y_personagem))
        
        pygame.display.flip()

        
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

def salvar_recorde(nome, pontuacao, dificuldade):
    df = pd.DataFrame({"Nome": [nome], "Pontuação": [pontuacao], "Dificuldade": [dificuldade]})
    try:
        df_existente = pd.read_excel("recordes.xlsx")
        df = pd.concat([df_existente, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_excel("recordes.xlsx", index=False)

if __name__ == "__main__":
    nome, senha, dificuldade = tela_inicial()
    jogo(nome, dificuldade)
    pygame.quit()