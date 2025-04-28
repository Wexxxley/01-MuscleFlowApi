import csv

def find_new_id_user():
    return contar_linhas_csv('data/users.csv') + 1

def find_new_id_exercise():
    return contar_linhas_csv('data/exercise.csv') + 1

def find_new_id_executed_daily_training():
    return contar_linhas_csv('data/executed_daily_training.csv') - 1

def contar_linhas_csv(caminho_arquivo: str):
    with open(caminho_arquivo, mode='r', newline='', encoding='utf-8') as arquivo: 
        leitor = csv.reader(arquivo)
        linhas = list(leitor)
        return len(linhas)
    
def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i

def get_all_valid_exercise_ids() -> set:
    with open('data/exercise.csv', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        return {int(row[0]) for row in reader}  
