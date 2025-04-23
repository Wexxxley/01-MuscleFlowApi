import csv

def find_new_id_user():
    return contar_linhas_csv('data/users.csv') + 1

def find_new_id_exercise():
    return contar_linhas_csv('data/exercise.csv') + 1

def contar_linhas_csv(caminho_arquivo: str):
    with open(caminho_arquivo, mode='r', newline='', encoding='utf-8') as arquivo: 
        leitor = csv.reader(arquivo)
        linhas = list(leitor)
        return len(linhas)
