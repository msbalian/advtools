# Chat Conversation

Note: _This is purely the output of the chat conversation and does not contain any raw data, codebase snippets, etc. used to generate the output._

### User Input

@[/brainstorm]
estude a api do datajud:
https://datajud-wiki.cnj.jus.br/api-publica/endpoints
Quero que, ao puxar os andamentos de um processo, preciso ter acesso ao conteúdo gerado em cada andamento, como por exemplo um despacho de um juiz dando prazo para um recurso. Isso é possível? O que sugere para conseguirmos isso, num primeiro momento pensando nos processos do PROJUDI, principalmente do TJGO. Claro que o ideal seria de mais tribunais e sistemas importantes.
Vi essa URL, não sei se ajuda nisso:
https://transparencia.tjgo.jus.br/ti-comunicacoes/acesso-automatizado


*Read URL content from /api-publica/endpoints *

*Read URL content from /ti-comunicacoes/acesso-automatizado *

*Searched web for Datajud API baixar documentos processos inteiro teor*

*Viewed [content.md](file:///C:/Users/PHDL/.gemini/antigravity/brain/202dedee-7a59-4900-aed3-5d0859f9527b/.system_generated/steps/6/content.md) *

*Searched web for TJGO acesso automatizado projudi API*

### Planner Response

## 🧠 Brainstorm: Acesso ao Inteiro Teor de Andamentos Judiciais (Datajud e PROJUDI TJGO)

### Context
A **API do Datajud** foi desenhada pelo CNJ para fins estatísticos e de pesquisa jurisdicional. Por questões de segurança, LGPD e limites de tráfego, ela **não fornece o "inteiro teor"** (o texto e os PDFs dos despachos, sentenças ou petições). Ela retorna apenas os *metadados* do processo (capa, partes, e a lista com os nomes e datas das movimentações). 
Para você acessar o conteúdo gerado em cada andamento (como ler que o juiz deu 5 dias para recurso), o sistema precisa ir "na fonte", ou seja, interagir diretamente com os sistemas originais (neste caso, o PROJUDI do TJGO). A URL que você enviou do TJGO de Fato descreve as regras de como eles lidam com tráfego massivo e oferecem endpoints via WebService.

Aqui estão as 3 opções para implementar essa extração de conteúdo:

---

### Option A: Automação via Web Scraping / RPA (Robotic Process Automation)
Utilizar ferramentas de automação de navegadores (como Playwright, Puppeteer ou Selenium) para criar robôs que logam no portal do PROJUDI TJGO (usando credenciais padrão de advogado/OAB ou certificado digital em nuvem). O robô navega no processo e extrai os textos HTML e baixa os PDFs.

✅ **Pros:**
- **Poder Total:** Você consegue ler e extrair 100% da informação que um humano veria.
- **Processos em Segredo:** Se a credencial do advogado estiver habilitada nos autos, o robô consegue ler processos sigilosos.
- **Não depende de burocracia do Tribunal:** Não precisa pedir chave de API oficial ou firmar convênios.

❌ **Cons:**
- **Manutenção Constante:** Se a equipe de TI do TJGO mudar um botão ou campo no site, seu robô quebra e precisa de manutenção.
- **Bloqueios e Captchas:** Tribunais costumam instalar firewalls (Cloudflare, etc) e Captchas dinâmicos contra robôs, exigindo soluções de proxy ou anti-captcha.
- **Desempenho:** É lento em comparação com uma requisição HTTP direta de API.

📊 **Effort:** Medium a High (alto custo de manutenção)

---

### Option B: Integração Oficial Direta (WebServices do Tribunal / MNI)
O TJGO e outros tribunais fornecem endpoints de WebService legados ou baseados no MNI (Modelo Nacional de Interoperabilidade). A URL que você informou cita o fornecimento de acessos automatizados (geralmente via WSDL/SOAP) para consumo de consultas públicas ou acesso a partes conveniadas (ex. PGM, PGE, Defensoria ou através de chaves cedidas para Lawtechs homologadas).

✅ **Pros:**
- **Estabilidade:** Sendo um meio de comunicação automatizado e oficial, tem "contrato de interface", então não quebra do nada como o web scraping.
- **Alta Velocidade:** Retorno em JSON ou XML bem rápido e de baixo impacto para a infraestrutura.

❌ **Cons:**
- **Burocracia de Acesso:** Em 99% das vezes, para pegar o inteiro teor como terceiro (Lawtech), exige-se um credenciamento no Tribunal ou CNJ para obter as Chaves e Tokens.
- **Falta de Padronização no Brasil:** O que funciona para o TJGO (Projudi) será completamente diferente do TJSP (e-Saj), que será diferente do TRT (PJe).

📊 **Effort:** High (burocraticamente e mapeamento de documentação técnica)

---

### Option C: Consumo de APIs de Datalawyers Terceiros (Lawtechs Fornecedoras)
Contratar plataformas do tipo "Legal Data as a Service" (Escavador, Digesto, Kurier, Aviso Urgente, Jusbrasil). Você envia apenas o número do CNJ pela API deles, e eles devolvem tudo: a árvore, o inteiro teor dos diários, e muitas vezes até cópia das peças já que os robôs deles (Option A) já fizeram o trabalho sujo.

✅ **Pros:**
- **Time-to-market Imediato:** Em 1 dia sua aplicação está extraindo dados de qualquer tribunal do país.
- **Hub Único:** Você se conecta em uma API RESTful bonita e limpa e não precisa ficar entendendo a arquitetura louca do PROJUDI, depois do PJe, depois do e-SAJ.
- **Zero manutenção de robôs.**

❌ **Cons:**
- **Custo contínuo:** Geralmente cobram por consulta do processo/andamento.
- **Processos em Segredo:** Caso não se ceda as credenciais OAB para a plataforma terceira, eles só conseguirão pegar os andamentos de processos 100% públicos.

📊 **Effort:** Low

---

## 💡 Recommendation

**Option A (RPA + Playwright)** ou **Option C (API Terceira)**.

**Por quê?** 
Depende do momento do seu negócio. 
Se você precisa validar a ideia, provar o conceito e construir rápido para focar na inteligência e UX do `Advtools` sem se frustrar com bloqueios, vá na **Option C** (assinar algum provider baratinho de base judiciária pra começar).

Se a estratégia da inteligência é internalizar essa tecnologia e não pagar terceiros, então vá de **Option A**. Criar nossos próprios scripts em *Playwright* orquestrados via filas (RabbitMQ/BullMQ) é como a maioria das grandes Lawtechs independentes nasceram antes do sistema atual ser mais integrado.

Qual direção ou caminho você gostaria de explorar ou focar para essa funcionalidade no sistema?

### User Input

Como hoje temos a IA para ajudar na manutenção constante, vamos de opção A e cresceremos nosso poder até nos tornar uma dessas lawtechs, mas com uma camada pronta ao escritório (advtools). o que acha? por onde vamos começar? Acha que podemos usar uma abordagem usando a consulta pública do dataJud como descoberta de movimentações e, a partir daí, entrar com o  Web Scraping / RPA? Me ajude a organizar as ideias

*Edited relevant file*

### Planner Response

Organizei nossas ideias no documento de planejamento (`implementation_plan.md` que acabou de aparecer para você).

A sua ideia de usar o **Datajud como um "Olheiro" (webhook natural) e o RPA como "Extrator"** é o "Santo Graal" das operações judiciais eficientes. Empresas que apenas fazem scraping sofrem com bloqueios de IP e servidores caros rodando 24/7 inutilmente. A sua abordagem garante que a gente só vá "bater" na porta do Tribunal quando soubermos que há uma atualização real esperando.

A arquitetura para o `advtools` ficaria fundamentada em três pequenos motores rodando no backend:

1. **O Olheiro:** Constantemente perguntando pro Datajud: *"O processo X andou?"*. É uma requisição leve de API, então não gera custos altos.
2. **O Despachante (Mensageria):** O Datajud diz que sim. O Despachante cria um "ticket de serviço" na nossa fila e fala: *"Vai lá no TJGO e baixa a movimentação nova desse processo"*.
3. **O Extrator (RPA):** Um robô em Playwright invisível engrena, faz o login no portal PROJUDI, busca cirurgicamente pelo arquivo/despacho, baixa, decodifica o PDF e salva no nosso cofre digital.

Dê uma lida atenta ao documento de plano de ação. As principais decisões que eu deixei em aberto para discutirmos são:

1. **Stack do Robô (Python vs Node.js):** Nosso backend já é em Python (FastAPI). Sugiro mantermos as provas de conceito no Playwright-Python para ficar um monólito elegante por agora. Você topa?
2. **Início Prático:** Quer que eu escreva algum script hoje de **Prova de Conceito (PoC)** isolado (tipo um `test_datajud.py` que bate na API do CNJ pra pegarmos um JSON oficial e ver a estrutura) ou fazemos um `test_rpa_tjgo.py` pra testar o login limpo primeiro?

### User Input

O que acha de dar o número da OAB do advogado, selecionar um TJ (ex: TJGO) e o sistema já faz o olheiro, trazendo para a plataforma todos os processos desse advogado neste tribunal como monitorados.
Em seguida, ainda na prova de conceito, podemos selecionar um dos processos, ver os andamentos e clicar para puxar o inteiro teor de um andamento, o que validaria a prova de conceito da atuação do robô no PROJUDI do TJ-GO.
Quero usar Python sempre que puder, com certeza

*Searched web for Datajud API Publica buscar por advogado OAB*

*Searched web for Datajud API pública consulta por nome advogado OAB LGPD*

*Edited relevant file*

### Planner Response

Excelente linha de raciocínio. Fui a fundo nas documentações públicas do CNJ e notei um detalhe muito importante arquiteturalmente: por questões da LGPD, a API do DataJud bloqueia buscas de processos massivas através de dados pessoais (como o Nome do Advogado ou OAB). Ela só permite busca rápida e passiva através do número exato do CNJ do processo em questão.

Isso invalida a ideia inicial, certo? **De forma alguma!** Na verdade nós vamos usar isso a nosso favor para criarmos aquela experiência sensacional "digitou a OAB, o sistema faz o resto":

1. **Descoberta via Robô (Primeiro Contato):** Na primeira vez, nós mandamos o robô em Python (Scraping/Playwright) logar diretamente na base do Tribunal de origem (ex: TJGO) e fazemos a consulta *interna* lá via OAB do advogado. O robô irá "raspar" todos os números unificados de processo (CNJs) em que aquele OAB atua e guarda no nosso banco (Advtools).
2. **Monitoramento via API (Econômico):** A partir daí o "Olheiro" do DataJud entra em cena. Agora que já sabemos os CNJs na nossa base, ele pode monitorá-los diariamente via API (o que é permitido e super barato computacionalmente), sem precisar rodar o peso do layout e browser de um Playwright toda hora.
3. **Extração de Conteúdo (Pontual):** Quando o olheiro acusar que um dos CNJs listados teve atualização (despacho na data de hoje), a gente acorda novamente o robô RPA do Playwright pra logar no TJGO e baixar *exclusivamente* o PDF/texto daquele andamento.

Eu escrevi e estruturei toda essa dinâmica de PoC nova no seu arquivo **`implementation_plan.md`** ao lado da tela. Isso define uma estrutura sólida, confiável e barata para suportar isso no futuro e evita os capangas e capchas de tribunais!

Veja se o documento faz sentido. Se estiver aprovado e o fluxo for esse mesmo, para dispararmos a prova de conceito do Python, me diga: a URL inicial do projudi em GO é através do `https://projudi.tjgo.jus.br` e você tem uma credencial fake/valida para logarmos no script via OAB? Vamos organizar nosso `/brainstorm` e dar o pontapé no código!