# 🚀 SkillSync API

API backend completa para o sistema SkillSync - Análise inteligente de currículos e compatibilidade com vagas.

## 🏗️ Arquitetura

### **Camadas da Aplicação**

```
📁 skillsync-api/
├── app/
│   ├── api/                    # 🌐 Camada de API (Endpoints)
│   │   ├── auth.py            # Autenticação e autorização
│   │   ├── resumes.py         # Gestão de currículos
│   │   ├── analysis.py        # Análises de compatibilidade
│   │   └── dashboard.py       # Dashboard e estatísticas
│   │
│   ├── services/              # 🔧 Camada de Serviços (Lógica de Negócio)
│   │   ├── user_service.py    # Gestão de usuários
│   │   ├── analysis_service.py # Análises e IA
│   │   ├── ai_service.py      # Integração com OpenAI
│   │   └── file_service.py    # Gestão de arquivos
│   │
│   ├── models/                # 📋 Camada de Domínio (Entidades)
│   │   └── domain.py          # Modelos de domínio
│   │
│   ├── dto/                   # 📦 Data Transfer Objects
│   │   ├── requests.py        # DTOs de entrada
│   │   └── responses.py       # DTOs de saída
│   │
│   ├── data/                  # 🗄️ Camada de Dados (Repositórios)
│   │   ├── sql_repository.py  # Repositório SQL Server
│   │   └── mongo_repository.py # Repositório MongoDB
│   │
│   ├── core/                  # ⚙️ Configurações e Utilitários
│   │   ├── config.py          # Configurações da aplicação
│   │   └── dependencies.py    # Dependências do FastAPI
│   │
│   └── main.py               # 🎯 Aplicação principal
```

## 🛠️ Tecnologias Utilizadas

### **Framework e Servidor**
- **FastAPI** - Framework web moderno e rápido
- **Uvicorn** - Servidor ASGI de alta performance
- **Pydantic** - Validação de dados e serialização

### **Bancos de Dados**
- **SQL Server** - Dados estruturados e relacionais
- **MongoDB** - Dados flexíveis e documentos JSON
- **Redis** - Cache e sessões

### **Integrações**
- **OpenAI GPT-4** - Análise inteligente de currículos
- **Azure Blob Storage** - Armazenamento de arquivos
- **Azure Cognitive Services** - Processamento de texto

### **Autenticação e Segurança**
- **JWT** - Tokens de autenticação
- **Bcrypt** - Hash de senhas
- **CORS** - Controle de acesso cross-origin

## 🚀 Instalação e Configuração

### **1. Pré-requisitos**
```bash
# Python 3.11+
python --version

# SQL Server (local ou Azure)
# MongoDB (local ou Atlas)
# Redis (opcional, para cache)
```

### **2. Clonar e Instalar**
```bash
# Clonar repositório
git clone <repository-url>
cd skillsync-api

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### **3. Configurar Ambiente**
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
nano .env
```

### **4. Configurar Bancos de Dados**

#### **SQL Server**
```bash
# Executar script de criação
sqlcmd -S localhost -d SkillSync -i ../skillsync-database-sqlserver.sql
```

#### **MongoDB**
```bash
# Executar script de configuração
mongosh skillsync ../skillsync-database-mongodb.js
```

### **5. Executar Aplicação**
```bash
# Desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 Documentação da API

### **Endpoints Principais**

#### **🔐 Autenticação**
```http
POST /api/v1/auth/register     # Registrar usuário
POST /api/v1/auth/login        # Login
POST /api/v1/auth/refresh      # Renovar token
GET  /api/v1/auth/profile      # Perfil do usuário
POST /api/v1/auth/change-password # Alterar senha
```

#### **📄 Currículos**
```http
GET    /api/v1/resumes         # Listar currículos
POST   /api/v1/resumes         # Criar currículo
GET    /api/v1/resumes/{id}    # Obter currículo
PUT    /api/v1/resumes/{id}    # Atualizar currículo
DELETE /api/v1/resumes/{id}    # Deletar currículo
POST   /api/v1/resumes/upload  # Upload de arquivo
```

#### **🔍 Análises**
```http
GET  /api/v1/analyses          # Listar análises
POST /api/v1/analyses          # Criar análise
GET  /api/v1/analyses/{id}     # Obter análise detalhada
POST /api/v1/analyses/bulk     # Análise em lote
```

#### **📊 Dashboard**
```http
GET /api/v1/dashboard/stats    # Estatísticas do usuário
GET /api/v1/dashboard/recent   # Atividades recentes
```

### **Documentação Interativa**
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔧 Configurações Avançadas

### **Variáveis de Ambiente**

```bash
# Aplicação
DEBUG=True                     # Modo debug
SECRET_KEY=your-secret-key     # Chave secreta JWT
HOST=0.0.0.0                   # Host do servidor
PORT=8000                      # Porta do servidor

# SQL Server
SQL_SERVER=localhost           # Servidor SQL
SQL_DATABASE=SkillSync         # Nome do banco
SQL_USERNAME=sa                # Usuário
SQL_PASSWORD=password          # Senha

# MongoDB
MONGO_URL=mongodb://localhost:27017  # URL de conexão
MONGO_DATABASE=skillsync       # Nome do banco

# OpenAI
OPENAI_API_KEY=sk-...          # Chave da API
OPENAI_MODEL=gpt-4-turbo-preview # Modelo a usar

# Azure Storage
AZURE_STORAGE_ACCOUNT=account  # Nome da conta
AZURE_STORAGE_KEY=key          # Chave de acesso
```

### **Configuração de Produção**

```bash
# Usar variáveis de ambiente seguras
export SECRET_KEY=$(openssl rand -hex 32)
export DEBUG=False

# Configurar HTTPS
export FORCE_HTTPS=True

# Configurar workers
export WORKERS=4
export MAX_REQUESTS=1000
```

## 🧪 Testes

### **Executar Testes**
```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/test_auth.py
pytest tests/test_analysis.py

# Com cobertura
pytest --cov=app tests/
```

### **Testes de Carga**
```bash
# Instalar locust
pip install locust

# Executar testes de carga
locust -f tests/load_test.py --host=http://localhost:8000
```

## 📈 Monitoramento

### **Health Check**
```bash
curl http://localhost:8000/health
```

### **Métricas**
```bash
curl http://localhost:8000/metrics
```

### **Logs**
```bash
# Logs em tempo real
tail -f logs/skillsync.log

# Logs estruturados
grep "ERROR" logs/skillsync.log | jq .
```

## 🔒 Segurança

### **Autenticação JWT**
- Tokens com expiração configurável
- Refresh tokens para renovação automática
- Blacklist de tokens revogados

### **Validação de Dados**
- Pydantic para validação automática
- Sanitização de inputs
- Rate limiting por usuário

### **Proteção de Dados**
- Hash bcrypt para senhas
- Criptografia de dados sensíveis
- Logs sem informações pessoais

## 🚀 Deploy

### **Docker**
```bash
# Build da imagem
docker build -t skillsync-api .

# Executar container
docker run -p 8000:8000 --env-file .env skillsync-api
```

### **Docker Compose**
```bash
# Subir todos os serviços
docker-compose up -d

# Logs
docker-compose logs -f api
```

### **Azure App Service**
```bash
# Deploy direto
az webapp up --name skillsync-api --resource-group skillsync-rg
```

## 📊 Performance

### **Benchmarks**
- **Throughput**: ~1000 req/s (single worker)
- **Latência**: ~50ms (análises simples)
- **Memória**: ~200MB (base)

### **Otimizações**
- Connection pooling para bancos
- Cache Redis para consultas frequentes
- Processamento assíncrono para IA
- CDN para arquivos estáticos

## 🤝 Contribuição

### **Padrões de Código**
```bash
# Formatação
black app/
isort app/

# Linting
flake8 app/
mypy app/

# Testes
pytest tests/
```

### **Estrutura de Commits**
```
feat: adicionar endpoint de análise em lote
fix: corrigir validação de upload de arquivo
docs: atualizar documentação da API
test: adicionar testes para serviço de IA
```

## 📝 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**SkillSync API - Transformando currículos em oportunidades! 🎯**
