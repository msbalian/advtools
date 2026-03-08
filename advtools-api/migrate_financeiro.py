import asyncio
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import AsyncSessionLocal
import models

async def migrate_payments():
    print("Iniciando migração de pagamentos...")
    async with AsyncSessionLocal() as db:
        # Busca todos os serviços que possuem condicoes_pagamento
        result = await db.execute(select(models.Servico).where(models.Servico.condicoes_pagamento != None))
        servicos = result.scalars().all()
        
        count = 0
        for s in servicos:
            try:
                pagamentos = json.loads(s.condicoes_pagamento)
                if not isinstance(pagamentos, list):
                    continue
                
                for p in pagamentos:
                    # Formato esperado no JSON: {"valor": 100, "data": "DD/MM/AAAA", ...}
                    valor = float(p.get('valor') or 0)
                    data_str = p.get('data')
                    
                    if not valor or not data_str:
                        continue
                        
                    try:
                        data_vencimento = datetime.strptime(data_str, "%d/%m/%Y")
                    except ValueError:
                        print(f"Data inválida ignorada: {data_str}")
                        continue
                    
                    # Verifica se já existe uma transação similar para evitar duplicidade (idempotência básica)
                    check_q = select(models.Transacao).where(
                        models.Transacao.servico_id == s.id,
                        models.Transacao.valor == valor,
                        models.Transacao.data_vencimento == data_vencimento
                    )
                    check_res = await db.execute(check_q)
                    if check_res.scalars().first():
                        continue
                    
                    nova_transacao = models.Transacao(
                        escritorio_id=s.escritorio_id,
                        cliente_id=s.cliente_id,
                        servico_id=s.id,
                        tipo="Receita",
                        categoria="Assessoria Jurídica",
                        valor=valor,
                        descricao=f"Parcela de serviço: {s.descricao or 'Serviço'}",
                        status="Pendente",
                        data_vencimento=data_vencimento
                    )
                    db.add(nova_transacao)
                    count += 1
            except Exception as e:
                print(f"Erro ao processar serviço {s.id}: {e}")
                
        await db.commit()
        print(f"Migração concluída! {count} transações criadas.")

if __name__ == "__main__":
    asyncio.run(migrate_payments())
