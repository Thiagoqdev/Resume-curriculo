# 🏗️ Arquitetura SkillSync - Responsabilidade Única por Camada

## 📋 Índice
1. [Introdução](#introdução)
2. [Por que Responsabilidade Única?](#por-que-responsabilidade-única)
3. [Nossa Arquitetura em Camadas](#nossa-arquitetura-em-camadas)
4. [Responsabilidades de Cada Camada](#responsabilidades-de-cada-camada)
5. [Exemplo Prático: Rota `/register`](#exemplo-prático-rota-register)
6. [Vantagens da Nossa Abordagem](#vantagens-da-nossa-abordagem)
7. [Problemas de Não Seguir Responsabilidade Única](#problemas-de-não-seguir-responsabilidade-única)
8. [Boas Práticas](#boas-práticas)
9. [Conclusão](#conclusão)

---

## 🎯 Introdução

O projeto **SkillSync API** segue uma arquitetura em camadas baseada no princípio da **Responsabilidade Única**. Cada camada tem uma função específica e bem definida, garantindo código limpo, testável e fácil de manter.

### 🎯 Objetivo
- **Organização**: Cada coisa no seu lugar
- **Manutenibilidade**: Fácil de modificar e estender
- **Testabilidade**: Cada camada pode ser testada isoladamente
- **Escalabilidade**: Fácil adicionar novas funcionalidades

---

## 🤔 Por que Responsabilidade Única?

### 🚨 **Problema: Código com Responsabilidades Misturadas**

```python
# ❌ ERRADO - API fazendo tudo misturado
@router.post("/register")
async def register_user(request: UserRegisterRequest):
    # ❌ API acessando banco diretamente
    if db.query("SELECT * FROM users WHERE email = ?", request.email):
        return {"erro": "Email já existe"}
    
    # ❌ API fazendo validação de negócio
    if len(request.full_name) < 2:
        return {"erro": "Nome muito curto"}
    
    # ❌ API fazendo hash de senha
    password_hash = bcrypt.hash(request.password)
    
    # ❌ API montando SQL diretamente
    db.execute("INSERT INTO users...")
    
    return {"user_id": "123", "email": request.email}
```

### 🔥 **Por que isso é PROBLEMÁTICO?**

1. **🚨 Violação do Princípio da Responsabilidade Única**
   - A API está fazendo MUITAS coisas: receber, validar, acessar banco, fazer hash, montar SQL, tratar erros, montar resposta

2. **🚨 Acoplamento Forte (Tight Coupling)**
   - API conhece detalhes do banco de dados
   - Se trocar de MySQL para PostgreSQL, a API quebra
   - Se trocar de bcrypt para argon2, a API quebra

3. **🚨 Impossível Testar Isoladamente**
   - Para testar a API, precisa de banco real, configurações, dados de teste
   - Testes lentos, frágeis e complexos

4. **🚨 Regras de Negócio Espalhadas**
   - Validações em vários lugares (API, frontend, service)
   - Se a regra mudar, tem que mudar em 3 lugares

5. **🚨 Difícil de Manter**
   - Uma mudança simples vira um pesadelo
   - Para adicionar validação de telefone, precisa modificar API, validação, banco, resposta, testes, documentação

---

## 🏗️ Nossa Arquitetura em Camadas

```
📁 skillsync-api-complete/
├── 🌐 api/                    # Interface Externa (Endpoints)
├── 📋 schemas/               # Contratos de Dados (DTOs) - Data Transfer Object (Objeto de Transferência de Dados)
│   ├── requests/             # DTOs de entrada
│   │   └── requests.py       # Todos os DTOs de requisição
│   └── responses/            # DTOs de saída
│       ├── responses.py      # DTOs gerais de resposta
│       ├── user_responses.py # DTOs específicos de usuário
│       ├── resume_responses.py # DTOs específicos de currículo
│       └── analysis_responses.py # DTOs específicos de análise
├── 🔄 mappers/               # Tradutores de Dados
├── ⚙️ services/              # Orquestradores (Lógica de Negócio)
├── 🏛️ domain/               # Coração do Sistema
│   ├── entities/            # Entidades de Domínio
│   └── factories/           # Fábricas de Objetos
├── 💾 data/                 # Camada de Persistência
│   ├── sql_repository.py    # SQL Server
│   └── mongo_repository.py  # MongoDB
├── 🔧 core/                 # Configurações e Utilitários
└── 🎯 main.py/app.py        # Aplicação Principal
```

---

## 🎯 Responsabilidades de Cada Camada

### 🌐 **Camada API (Interface Externa)**

**Responsabilidade**: Ser a "porta de entrada" do sistema

**✅ PODE fazer:**
- Receber requisições HTTP (GET, POST, PUT, DELETE)
- Validar formato básico (Pydantic faz isso)
- Chamar o Service apropriado
- Retornar resposta HTTP formatada
- Tratar erros de forma amigável

**❌ NÃO PODE fazer:**
- Acessar banco de dados diretamente
- Implementar regras de negócio
- Conhecer detalhes de como Entity funciona
- Fazer cálculos complexos
- Instanciar conexões de banco

**Exemplo:**
```python
# ✅ CORRETO
@router.post("/register", response_model=UserProfileResponse)
async def register_user(request: UserRegisterRequest):
    try:
        user_service = UserService()  # ← Chama Service
        user_profile = await user_service.register_user(request)
        return user_profile  # ← Retorna resposta
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

### 📋 **Camada Schemas (Contratos)**

**Responsabilidade**: Definir "contratos" de entrada e saída

**✅ PODE fazer:**
- Definir formato dos dados de entrada (Request)
- Definir formato dos dados de saída (Response)
- Validar tipos, tamanhos, formatos
- Documentar automaticamente a API
- Ter validations automáticas do Pydantic

**❌ NÃO PODE fazer:**
- Implementar lógica de negócio
- Acessar banco de dados
- Fazer cálculos complexos
- Depender de outras camadas (exceto tipos básicos)

**Exemplo:**
```python
# ✅ CORRETO
class UserRegisterRequest(BaseModel):
    """DTO para registro de usuário"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v
```

---

### 🔄 **Camada Mappers (Tradutores)**

**Responsabilidade**: Traduzir entre diferentes formatos de dados

**✅ PODE fazer:**
- Converte Entity (domínio) para Response (API)
- Permite diferentes "visões" dos mesmos dados
- Protege dados internos de vazarem para fora
- Criar múltiplas representações da mesma entidade

**❌ NÃO PODE fazer:**
- Implementar lógica de negócio
- Acessar banco de dados
- Fazer cálculos complexos
- Depender de outras camadas

**Exemplo:**
```python
# ✅ CORRETO
class UserMapper:
    @staticmethod
    def to_public(user: User) -> UserProfileResponse:
        """Converte entidade User para resposta pública"""
        return UserProfileResponse(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            subscription_type=user.subscription_type,
            created_at=user.created_at,
            email_verified=user.email_verified
        )
    
    @staticmethod
    def to_display(user: User) -> dict:
        """Converte para exibição simples"""
        return {
            "id": str(user.user_id),
            "name": user.full_name,
            "email": user.email,
            "subscription": user.subscription_type.value
        }
```

---

### ⚙️ **Camada Service (Orquestrador)**

**Responsabilidade**: Coordenar casos de uso complexos

**✅ PODE fazer:**
- Orquestrar fluxos de negócio
- Coordenar entre diferentes partes
- Validar regras que dependem de dados externos
- Controlar transações
- Usar helpers da Factory para extrair dados

**❌ NÃO PODE fazer:**
- Acessar campos do DTO diretamente (dto.nome)
- Conhecer detalhes de banco de dados
- Instanciar entidades diretamente
- Implementar validações que a Entity pode fazer
- Retornar DTOs (retorna Entities)

**Exemplo:**
```python
# ✅ CORRETO
async def register_user(self, request: UserRegisterRequest) -> UserProfileResponse:
    # 1. Verificar se email já existe
    if await self.user_repo.exists_email(request.email):
        raise ValueError("Email já existe")
    
    # 2. Criar usuário via Factory
    user = UserFactory.make_user(request)
    user.password_hash = self._hash_password(request.password)
    
    # 3. Salvar via Repository
    created_user = await self.user_repo.create_user(user)
    
    # 4. Converter via Mapper
    return UserMapper.to_public(created_user)
```

---

### 🏭 **Camada Factory (Fábrica)**

**Responsabilidade**: Criar objetos do domínio de forma consistente

**✅ PODE fazer:**
- Ser única porta de criação de entidades
- Fazer validações de criação
- Extrair dados de DTOs usando helpers
- Fornecer helpers para Service (email_from, id_from)
- Converter tipos de dados
- Gerar IDs únicos

**❌ NÃO PODE fazer:**
- Acessar banco de dados
- Depender de Repository
- Fazer validações que precisam de dados externos
- Retornar entidades parciais
- Ter múltiplas formas de criar a mesma entidade

**Exemplo:**
```python
# ✅ CORRETO
class UserFactory:
    @staticmethod
    def make_user(dto: Any) -> User:
        # Extrair dados usando helpers
        email = email_from(dto)
        full_name = name_from(dto)
        phone = phone_from(dto)
        
        # Validações específicas
        if len(full_name) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        
        if not email or "@" not in email:
            raise ValueError("Email deve ter formato válido")
        
        # Criar usuário
        return User(
            user_id=uuid4(),
            email=email.strip().lower(),
            full_name=full_name.strip(),
            phone=phone,
            subscription_type=SubscriptionType.FREE,
            created_at=datetime.utcnow(),
            is_active=True
        )
```

---

### 🏛️ **Camada Domain (Coração)**

**Responsabilidade**: Guardar as regras de negócio mais importantes

**✅ PODE fazer:**
- Definir entidades como dataclass
- Implementar comportamentos (ativar, desativar)
- Validar invariantes da entidade
- Aplicar regras de negócio puras
- Usar método aplicar_atualizacao_from_any()
- Ter propriedades calculadas

**❌ NÃO PODE fazer:**
- Importar Pydantic, FastAPI, SQLAlchemy
- Acessar banco de dados
- Ter @staticmethod criar() (só Factory cria)
- Depender de camadas externas
- Fazer validações que precisam de dados externos

**Exemplo:**
```python
# ✅ CORRETO
@dataclass
class User:
    """Entidade Usuário"""
    user_id: UUID
    email: str
    full_name: str
    password_hash: str
    phone: Optional[str] = None
    subscription_type: SubscriptionType = SubscriptionType.FREE
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    email_verified: bool = False
    
    def ativar(self) -> None:
        """Ativar usuário"""
        if not self.is_active:
            self.is_active = True
            self.updated_at = datetime.utcnow()
    
    def desativar(self) -> None:
        """Desativar usuário"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def aplicar_atualizacao_from_any(self, data: Any) -> None:
        """Aplica mudanças de qualquer fonte de dados"""
        novo_nome = _get(data, "full_name")
        if novo_nome and len(novo_nome.strip()) >= 2:
            self.full_name = novo_nome.strip()
            self.updated_at = datetime.utcnow()
```

---

### 💾 **Camada Repository (Persistência)**

**Responsabilidade**: Guardar e buscar dados

**✅ PODE fazer:**
- Salvar/buscar/atualizar entidades
- Converter Entity ↔ Model (mapeamentos privados)
- Usar SQLAlchemy, MongoDB, etc.
- Fazer queries complexas quando necessário
- Implementar métodos como get_by_email, list, etc.

**❌ NÃO PODE fazer:**
- Implementar regras de negócio
- Validar dados (isso é do Domain)
- Conhecer detalhes de API ou DTOs
- Fazer cálculos de negócio
- Expor detalhes do banco para outras camadas

**Exemplo:**
```python
# ✅ CORRETO
class UserRepository:
    def __init__(self):
        self.engine = create_engine(settings.sql_connection_string)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    async def create_user(self, user: User) -> User:
        """Criar usuário no banco"""
        try:
            with self.get_session() as session:
                model = self._to_model(user)
                session.add(model)
                session.commit()
                return self._to_entity(model)
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def _to_entity(self, model: UserModel) -> User:
        """Converte banco → domínio"""
        return User(
            user_id=model.user_id,
            email=model.email,
            full_name=model.full_name,
            phone=model.phone,
            subscription_type=model.subscription_type,
            created_at=model.created_at,
            is_active=model.is_active
        )
    
    def _to_model(self, entity: User) -> UserModel:
        """Converte domínio → banco"""
        return UserModel(
            user_id=entity.user_id,
            email=entity.email,
            full_name=entity.full_name,
            phone=entity.phone,
            subscription_type=entity.subscription_type,
            created_at=entity.created_at,
            is_active=entity.is_active
        )
```

---

## 🔄 Exemplo Prático: Rota `/register`

Vamos ver como cada camada se comunica no fluxo completo:

### **1. 🌐 API recebe requisição**
```python
@router.post("/register", response_model=UserProfileResponse)
async def register_user(request: UserRegisterRequest):
    try:
        user_service = UserService()  # ← Delega para Service
        user_profile = await user_service.register_user(request)
        return user_profile  # ← Retorna resposta
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### **2. 📋 Schemas validam dados**
```python
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
```

### **3. ⚙️ Service orquestra processo**
```python
async def register_user(self, request: UserRegisterRequest) -> UserProfileResponse:
    # Verificar se email existe
    if await self.user_repo.exists_email(request.email):
        raise ValueError("Email já existe")
    
    # Criar usuário via Factory
    user = UserFactory.make_user(request)
    user.password_hash = self._hash_password(request.password)
    
    # Salvar via Repository
    created_user = await self.user_repo.create_user(user)
    
    # Converter via Mapper
    return UserMapper.to_public(created_user)
```

### **4. 🏭 Factory cria entidade**
```python
@staticmethod
def make_user(dto: Any) -> User:
    if len(dto.full_name) < 2:
        raise ValueError("Nome deve ter pelo menos 2 caracteres")
    
    return User(
        user_id=uuid4(),
        email=dto.email.strip().lower(),
        full_name=dto.full_name.strip(),
        phone=dto.phone,
        subscription_type=SubscriptionType.FREE,
        created_at=datetime.utcnow(),
        is_active=True
    )
```

### **5. 🏛️ Domain aplica regras**
```python
@dataclass
class User:
    user_id: UUID
    email: str
    full_name: str
    # ... outros campos
    
    def ativar(self) -> None:
        self.is_active = True
        self.updated_at = datetime.utcnow()
```

### **6. 💾 Repository salva dados**
```python
async def create_user(self, user: User) -> User:
    model = self._to_model(user)
    session.add(model)
    session.commit()
    return self._to_entity(model)
```

### **7. 🔄 Mapper converte resposta**
```python
@staticmethod
def to_public(user: User) -> UserProfileResponse:
    return UserProfileResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        subscription_type=user.subscription_type,
        created_at=user.created_at,
        email_verified=user.email_verified
    )
```

### **8. 🌐 API retorna resposta**
```python
# Retorna UserProfileResponse para o cliente
```

---

## ✅ Vantagens da Nossa Abordagem

### **1. 🎯 Responsabilidade Única**
- Cada camada tem uma função específica e bem definida
- Fácil entender o que cada parte faz
- Mudanças ficam isoladas em suas respectivas camadas

### **2. 🔗 Desacoplamento**
- Camadas não conhecem detalhes internas umas das outras
- Pode trocar implementações sem afetar outras camadas
- API não conhece banco, Service não conhece HTTP

### **3. 🧪 Testabilidade**
- Cada camada pode ser testada isoladamente
- Testes rápidos, confiáveis e isolados
- Mock de dependências é simples

### **4. 📋 Regras Centralizadas**
- Validações em um lugar só
- Mudança de regra = mudança em um lugar
- Consistência em todo o sistema

### **5. 🚀 Facilidade de Manutenção**
- Mudanças simples e controladas
- Fácil adicionar novas funcionalidades
- Código limpo e organizado

### **6. 📈 Escalabilidade**
- Fácil adicionar novas funcionalidades
- Pode crescer sem quebrar o que já existe
- Equipe pode trabalhar em paralelo

---

## 🚨 Problemas de Não Seguir Responsabilidade Única

### **1. 🚨 Código Bagunçado**
```python
# ❌ Tudo misturado em um lugar
@router.post("/register")
async def register_user(request: UserRegisterRequest):
    # Validação
    if len(request.full_name) < 2:
        return {"erro": "Nome muito curto"}
    
    # Acesso ao banco
    if db.query("SELECT * FROM users WHERE email = ?", request.email):
        return {"erro": "Email já existe"}
    
    # Hash de senha
    password_hash = bcrypt.hash(request.password)
    
    # SQL
    db.execute("INSERT INTO users...")
    
    # Resposta
    return {"user_id": "123", "email": request.email}
```

### **2. 🚨 Impossível Testar**
- Precisa de banco real para testar
- Configurações complexas
- Testes lentos e frágeis

### **3. 🚨 Regras Espalhadas**
- Validações em vários lugares
- Inconsistências
- Difícil manter

### **4. 🚨 Difícil Manutenção**
- Uma mudança quebra tudo
- Código difícil de entender
- Equipe trava

---

## 🎓 Boas Práticas

### **1. 🎯 Regra de Ouro**
> **"Cada camada deve ter UMA responsabilidade e NÃO deve conhecer detalhes das outras camadas"**

### **2. 🔄 Fluxo de Dados**
```
API → Service → Factory → Domain → Repository
  ↑                                    ↓
  ← Mapper ← Service ← Factory ← Domain ←
```

### **3. 📋 Checklist para Cada Camada**

#### **🌐 API:**
- [ ] Só recebe e retorna HTTP
- [ ] Chama Service
- [ ] Trata exceções
- [ ] NÃO acessa banco
- [ ] NÃO implementa regras

#### **📋 Schemas:**
- [ ] Define contratos
- [ ] Valida formatos
- [ ] Documenta API
- [ ] NÃO implementa lógica

#### **⚙️ Service:**
- [ ] Orquestra processo
- [ ] Coordena camadas
- [ ] Valida regras externas
- [ ] NÃO acessa banco diretamente

#### **🏭 Factory:**
- [ ] Cria entidades
- [ ] Valida criação
- [ ] Fornece helpers
- [ ] NÃO acessa banco

#### **🏛️ Domain:**
- [ ] Regras de negócio
- [ ] Comportamentos
- [ ] Validações puras
- [ ] NÃO depende de camadas externas

#### **💾 Repository:**
- [ ] Acessa dados
- [ ] Converte formatos
- [ ] Implementa queries
- [ ] NÃO implementa regras

#### **🔄 Mapper:**
- [ ] Converte formatos
- [ ] Protege dados
- [ ] Cria visões
- [ ] NÃO implementa lógica

### **4. 🧪 Testes por Camada**

```python
# Teste da API (mock do Service)
def test_register_user_api():
    mock_service = Mock()
    mock_service.register_user.return_value = UserProfileResponse(...)
    
    response = client.post("/register", json={...})
    assert response.status_code == 200

# Teste do Service (mock do Repository)
def test_register_user_service():
    mock_repo = Mock()
    mock_repo.exists_email.return_value = False
    
    service = UserService()
    result = service.register_user(request)
    assert result.email == "test@example.com"

# Teste da Factory (sem dependências)
def test_make_user_factory():
    dto = {"email": "test@example.com", "full_name": "Test User"}
    user = UserFactory.make_user(dto)
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
```

---

## 🎯 Conclusão

A arquitetura com **Responsabilidade Única** do SkillSync garante:

### **✅ Benefícios Imediatos:**
- Código organizado e limpo
- Fácil de entender e manter
- Testes rápidos e confiáveis
- Regras centralizadas

### **✅ Benefícios a Longo Prazo:**
- Fácil adicionar funcionalidades
- Equipe pode trabalhar em paralelo
- Mudanças controladas
- Sistema escalável

### **🎓 Para os Alunos:**
> **"Lembre-se: cada camada tem UMA função. Se uma camada está fazendo mais de uma coisa, você está violando o princípio da responsabilidade única!"**

### **🚀 Próximos Passos:**
1. Implementar todas as camadas seguindo este padrão
2. Criar testes para cada camada
3. Documentar responsabilidades
4. Treinar a equipe nos padrões

---

**SkillSync API - Arquitetura Limpa e Responsável! 🎯**
