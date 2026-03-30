
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import models
from config import Config

DATABASE_URL = Config.DATABASE_URL.replace("+asyncpg", "")

def check_client_data():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Busca João Lino
    cliente = session.query(models.Cliente).filter(models.Cliente.nome.ilike("%João Lino%")).first()
    
    if cliente:
        print(f"Cliente: {cliente.nome}")
        print(f"  - nacionalidade: '{cliente.nacionalidade}'")
        print(f"  - estado_civil: '{cliente.estado_civil}'")
        print(f"  - profissao: '{cliente.profissao}'")
        print(f"  - rg: '{cliente.rg}'")
        print(f"  - endereco: '{cliente.endereco}'")
        print(f"  - bairro: '{cliente.bairro}'")
        print(f"  - cep: '{cliente.cep}'")
    else:
        print("Cliente não encontrado.")
    session.close()

if __name__ == "__main__":
    check_client_data()
