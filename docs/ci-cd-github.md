# Resumo da Implementação: GitHub Actions CI/CD 🚀

Finalizamos a criação do Workflow de Pipeline Contínuo para o projeto. Agora, sempre que o código for atualizado na branch `main`, sua VPS será devidamente sincronizada.

### 1. O que foi feito?
- Criamos o arquivo `deploy.yml` na pasta `.github/workflows` que o GitHub lê automaticamente.
- O pipeline foi configurado para conectar via **SSH** na sua VPS (`/var/www/advtools`).
- Ele automatiza o pull do git, a recriação das imagens em produção (`docker compose -f docker-compose.prod.yml build` e `up -d`).
- Por fim, executa o `alembic upgrade head` no container da API instanciada.

> [!WARNING]
> ### 2. Ação Necessária: Configurando as Chaves (Secrets)
> Para a VPS permitir a entrada do GitHub e para o Workflow não dar erro "Authentication failed", você precisa adicionar os Segredos no repositório.

Vá no repositório do projeto no site do GitHub, e acesse:
**Settings -> Secrets and variables -> Actions**, e então clique em **"New repository secret"** para adicionar os seguintes:

- Nome: `HOST_IP` | Valor: (Coloque o endereço IP da sua VPS, Ex: `198.51.100.1`)
- Nome: `SSH_USER` | Valor: (Coloque o seu usuário SSH, Ex: `root` ou `ubuntu`)
- Nome: `SSH_PRIVATE_KEY` | Valor: (Cole **toda** a sua chave privada SSH que tem permissão na VPS. Exemplo: o conteúdo do seu arquivo `~/.ssh/id_rsa` que começa com `-----BEGIN OPENSSH PRIVATE KEY-----...`).

> [!TIP]
> Se o seu usuário na VPS usar "senha" ao invés de "chave primária" SSH, avise-me, pois a configuração do Action necessitará usar o parâmetro "password: ${{ secrets.SSH_PASSWORD }}" em vez do "key". É altamente recomendável usar Chaves Privadas por segurança.

### 3. Como Disparar o Deploy?
Após configurar os Secrets, bastará realizar um commit normalmente adicionando o próprio arquivo `deploy.yml` que acabamos de criar, e enviá-lo com:

```bash
git add .
git commit -m "feat: configuracao CI/CD com Github Actions"
git push origin main
```

Após o push, vá à aba **"Actions"** no repositório do GitHub e acompanhe a bolinha girando até ficar **Verde** em Produção! Se ela ficar vermelha, você poderá abrir o respectivo Step do Job para ver qual erro aconteceu na conexão/atualização.
