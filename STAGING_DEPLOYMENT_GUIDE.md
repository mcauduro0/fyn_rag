# Guia de Deployment em Staging: Fyn RAG System

Este guia detalha o processo passo-a-passo para implantar o sistema Fyn RAG em um ambiente de staging utilizando **Railway** (para Backend e Banco de Dados) e **Vercel** (para Frontend).

## 1. Pré-requisitos

Certifique-se de ter acesso às seguintes contas e ferramentas:
- Conta no [GitHub](https://github.com) (com acesso ao repositório `mcauduro0/fyn_rag`)
- Conta no [Railway](https://railway.app)
- Conta na [Vercel](https://vercel.com)
- Credenciais de API (OpenAI, Anthropic, Polygon, FMP)

---

## 2. Backend & Database (Railway)

O Railway hospedará o serviço Python (FastAPI) e o banco de dados PostgreSQL.

### Passo 2.1: Criar Novo Projeto
1. Acesse o dashboard do Railway e clique em **"New Project"**.
2. Selecione **"Deploy from GitHub repo"**.
3. Escolha o repositório `mcauduro0/fyn_rag`.
4. **IMPORTANTE**: Não faça o deploy imediatamente. Clique em **"Add Variables"** ou configure as variáveis primeiro.

### Passo 2.2: Configurar PostgreSQL
1. No canvas do projeto, clique em **"New"** -> **"Database"** -> **"PostgreSQL"**.
2. Aguarde a criação do banco de dados.
3. O Railway criará automaticamente as variáveis de ambiente `DATABASE_URL`, `PGHOST`, `PGUSER`, etc.

### Passo 2.3: Configurar Serviço Backend
1. Selecione o serviço do repositório GitHub no canvas.
2. Vá em **"Settings"** -> **"Root Directory"** e defina como `/` (ou deixe em branco, pois o `railway.toml` está na raiz).
3. Vá em **"Variables"** e adicione as seguintes chaves (copie do seu `.env` local):
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `POLYGON_API_KEY`
   - `FMP_API_KEY`
   - `DATABASE_URL` (Use a variável de referência `${{Postgres.DATABASE_URL}}`)
   - `ENVIRONMENT=staging`

### Passo 2.4: Deploy
1. O Railway detectará automaticamente o arquivo `railway.toml` e o `backend/Dockerfile`.
2. O deploy iniciará. Acompanhe os logs em "Deployments".
3. Após o sucesso, vá em **"Settings"** -> **"Networking"** e gere um domínio público (ex: `fyn-rag-backend-production.up.railway.app`).
4. **Copie este domínio**, você precisará dele para o frontend.

---

## 3. Frontend (Vercel)

A Vercel hospedará a aplicação React e servirá os assets estáticos.

### Passo 3.1: Importar Projeto
1. Acesse o dashboard da Vercel e clique em **"Add New..."** -> **"Project"**.
2. Importe o repositório `mcauduro0/fyn_rag`.

### Passo 3.2: Configurar Build
1. Em **"Framework Preset"**, selecione **Vite**.
2. Em **"Root Directory"**, clique em "Edit" e selecione a pasta `frontend`.
3. As configurações de build devem ser detectadas automaticamente (`pnpm build`, `dist`).

### Passo 3.3: Variáveis de Ambiente
Adicione as seguintes variáveis:
- `VITE_API_URL`: Cole a URL do backend do Railway (ex: `https://fyn-rag-backend-production.up.railway.app`).
  *Nota: Certifique-se de não incluir a barra `/` no final se o seu código frontend não esperar por ela.*

### Passo 3.4: Deploy
1. Clique em **"Deploy"**.
2. A Vercel construirá o projeto e fornecerá uma URL de staging (ex: `fyn-rag-frontend.vercel.app`).

---

## 4. Validação End-to-End

Após ambos os deploys estarem ativos:

1. Acesse a URL do Frontend na Vercel.
2. Abra o console do navegador (F12) para monitorar erros de rede.
3. Tente iniciar uma nova análise na aba "Analysis".
4. Verifique se o backend no Railway recebe a requisição (logs do Railway).
5. Verifique se os dados são persistidos no banco de dados (aba "Data" no PostgreSQL do Railway).

## 5. Troubleshooting Comum

- **Erro CORS**: Se o frontend não conseguir falar com o backend, verifique se o backend (FastAPI) está configurado para aceitar a origem do frontend.
  - *Solução*: No `backend/app/main.py`, adicione a URL da Vercel na lista de `allow_origins` do `CORSMiddleware`.
- **Erro de Conexão DB**: Verifique se a variável `DATABASE_URL` no serviço backend está correta e se o serviço está na mesma rede privada do PostgreSQL no Railway.

---

**Suporte**: Para problemas específicos, consulte os logs de build em ambas as plataformas.
