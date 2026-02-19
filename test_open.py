
import os

# Caminho para os modelos
PASTA_MODELOS = r'd:/Projetos/advtools/modelos'

# Tenta listar os arquivos
try:
    arquivos = os.listdir(PASTA_MODELOS)
    docx_files = [f for f in arquivos if f.endswith('.docx')]
    
    if not docx_files:
        print("Nenhum arquivo .docx encontrado na pasta modelos.")
    else:
        arquivo_teste = docx_files[0]
        caminho_completo = os.path.join(PASTA_MODELOS, arquivo_teste)
        print(f"Tentando abrir: {caminho_completo}")
        
        try:
            os.startfile(caminho_completo)
            print("Sucesso! O arquivo deve ter aberto.")
        except Exception as e:
            print(f"Erro ao abrir arquivo: {e}")
            
except Exception as e:
    print(f"Erro ao listar pasta: {e}")
