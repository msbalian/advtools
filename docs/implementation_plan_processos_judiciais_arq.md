# Arquitetura de Captura de Processos Judiciais (DataJud + RPA)

A estratégia de utilizar a API do Datajud como um mecanismo de "descoberta" e acionar o Robô (RPA) apenas quando houver novidades é uma arquitetura de altíssimo nível. Ela reduz consideravelmente os custos de infraestrutura e evita bloqueios dos tribunais, pois o robô só fará o login quando houver a garantia de que uma nova movimentação, de fato, ocorreu.

Esta arquitetura híbrida é escalável, econômica e coloca o **Advtools** no caminho para se tornar um provedor robusto de dados judiciais (Lawtech).

## Arquitetura Proposta

A solução é composta por 3 engrenagens principais trabalhando em background:

### 1. O "Olheiro" (Integração Datajud)
- Um worker (job agendado) que roda periodicamente (ex: a cada 2 ou 6 horas).
- Ele pega a lista de processos (CNJs) cadastrados pelos advogados no sistema Advtools.
- Ele faz requisições passivas à **API Pública do Datajud**.
- Se a data de atualização do processo no Datajud for mais recente do que a registrada no nosso banco, ele lança um alerta: *"Temos andamentos novos neste CNJ!"*

### 2. O "Despachante" (Fila de Processamento)
- Em vez de rodar o robô imediatamente e travar o servidor, o Olheiro joga o aviso em uma fila (ex: banco de dados ou Redis/BullMQ).
- **Evento gerado:** `{ tipo: "BUSCAR_INTEIRO_TEOR", cnj: "xxxx-xx", tribunal: "TJGO" }`
- Isso permite retentativas caso o Datacenter do Tribunal esteja fora do ar.

### 3. O "Extrator" (RPA Playwright)
- Um worker isolado, rodando navegadores headless via **Playwright**.
- Ele escuta a fila. Quando recebe o processo, ele:
  1. Acessa o site do TJGO (PROJUDI).
  2. Loga (usando OAB/Senha ou Certificado armazenados de forma criptografada).
  3. Navega até os autos.
  4. Identifica e lê a nova movimentação.
  5. Extrai o texto da decisão (parsing HTML) ou baixa o PDF do despacho.
  6. Salva as informações de volta no banco do Advtools e os arquivos no storage (minIO / volume local).

---

## Estratégia de Desenvolvimento (Fases)

Para não construir tudo de uma vez e se frustrar, precisamos fragmentar em **Provas de Conceito (PoCs)**. 

### Fase 1: PoC do Olheiro (Datajud)
**Objetivo:** Provar que conseguimos consultar e analisar a árvore processual através da API sem o bloqueio.
- [ ] Obter a chave de acesso pública da API do Datajud.
- [ ] Criar um script isolado `poc_datajud.py` que consulta um processo conhecido.
- [ ] Tratar a resposta JSON e comparar hashes para detectar novos andamentos.

### Fase 2: PoC do Extrator (RPA TJGO)
**Objetivo:** Provar que o Playwright consegue transpor o login e baixar um documento do PROJUDI.
- [ ] Escolher uma linguagem de extração (Sugerido: TypeScript/Node.js para Playwright ou Python/Playwright).
- [ ] Criar um robô `poc_tjgo_scraper.py` que entra no TJGO (Autenticação OAB/Senha).
- [ ] Localizar as tags HTML corretas do andamento e fazer o download de um PDF conhecido sem ser barrado por Captcha.

### Fase 3: A "Cola" (Back-end)
**Objetivo:** Transformar os scripts em rotinas de background na arquitetura do Advtools (FastAPI).
- [ ] Criar a modelagem do banco (Tabela `processos_monitorados`, `andamentos_processo`, `fila_crawlers`).
- [ ] Configurar um agendador simples (Celery ou APScheduler ou TaskIQ no FastAPI) para rodar o Olheiro.
- [ ] Integrar o PoC do robô no agendador.

### Fase 4: O "Palco" (Front-end Vue.js)
**Objetivo:** Interface para o advogado tirar proveito.
- [ ] Tela "Adicionar Processo para Monitoramento".
- [ ] Timeline moderna renderizando o histórico e o botão de ler documento do andamento.
- [ ] IA (Opcional Futuro): Resumir o PDF baixado em 1 parágrafo ("O juiz deu 5 dias para cumprimento").

---

## User Review Required

> [!QUESTION] Perguntas de Definição
> 1. **Tecnologia do Robô:** Como já usamos Python no ecossistema (FastAPI) e Node/Vue no Front, podemos escrever as **PoCs** do robô tanto usando o Playwright em Python quanto Playwright em Node. Qual você prefere? (Python mantém o backend unificado).
> 2. **Por onde quer começar agora?** Quer que eu comece codando um script rápido de **Prova de Conceito (PoC) da Fase 1 (Datajud)** ou a **Fase 2 (RPA do TJGO)** para validarmos tecnicamente as integrações antes de sujar o código oficial da API?
