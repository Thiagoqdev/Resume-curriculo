# 🏗️ Plano de Refatoração - Arquitetura IT Valley

## 📋 Estrutura Atual vs Nova

### Estrutura Atual:
```
app/
├── api/           # ✅ Já existe
├── dto/           # ✅ Já existe (será movido para schemas/)
├── services/      # ✅ Já existe (será refatorado)
├── models/        # ✅ Já existe (será movido para domain/)
├── data/          # ✅ Já existe (será refatorado)
└── core/          # ✅ Já existe
```

### Nova Estrutura IT Valley:
```
app/
├── api/                    # 🌐 Camada API (FastAPI)
├── schemas/               # 📋 Contratos (DTOs)
│   ├── requests/          # DTOs de entrada
│   └── responses/         # DTOs de saída
├── mappers/               # 🔄 Tradutores (NOVO)
├── services/              # ⚙️ Orquestradores (REFATORAR)
├── domain/                # 🏛️ Coração do Sistema
│   ├── entities/          # Entidades
│   └── factories/         # Fábricas (NOVO)
├── data/                  # 💾 Persistência
│   ├── models/            # Models SQLAlchemy
│   └── repositories/      # Repositórios
├── integrations/          # 🤖 Integrações Externas
└── core/                  # ⚙️ Configurações
```

## 🎯 Plano de Implementação

### Fase 1: Reestruturação de Pastas
- [ ] Criar pasta `schemas/` e mover DTOs
- [ ] Criar pasta `mappers/` 
- [ ] Criar pasta `domain/` e mover models
- [ ] Criar pasta `domain/factories/`
- [ ] Criar pasta `integrations/`
- [ ] Reorganizar `data/` em `models/` e `repositories/`

### Fase 2: Implementar Mappers
- [ ] Criar `mappers/user_mapper.py`
- [ ] Criar `mappers/resume_mapper.py`
- [ ] Criar `mappers/analysis_mapper.py`
- [ ] Implementar métodos `to_public()`, `to_display()`, etc.

### Fase 3: Implementar Factories
- [ ] Criar `domain/factories/user_factory.py`
- [ ] Criar `domain/factories/resume_factory.py`
- [ ] Criar `domain/factories/analysis_factory.py`
- [ ] Implementar helpers `_get()`, `email_from()`, etc.

### Fase 4: Refatorar Services
- [ ] Refatorar `UserService` para seguir padrão IT Valley
- [ ] Refatorar `AnalysisService` para seguir padrão IT Valley
- [ ] Remover lógica de criação direta de entidades
- [ ] Usar Factories para criar entidades

### Fase 5: Refatorar Repositories
- [ ] Separar em `data/models/` e `data/repositories/`
- [ ] Implementar métodos `_to_entity()` e `_to_model()`
- [ ] Remover lógica de negócio dos repositories

### Fase 6: Atualizar API Endpoints
- [ ] Refatorar endpoints para usar Mappers
- [ ] Implementar dependency injection correta
- [ ] Seguir padrão: API → Service → Factory → Domain → Repository

## 🔧 Implementações Específicas

### 1. Helpers Globais
```python
# domain/helpers.py
def _get(data: Any, key: str, default: Any = None) -> Any:
    """Helper para extrair dados de forma segura"""
    if hasattr(data, key):
        return getattr(data, key)
    elif isinstance(data, dict):
        return data.get(key, default)
    return default
```

### 2. Factory Pattern
```python
# domain/factories/user_factory.py
class UserFactory:
    @staticmethod
    def make_user(dto: Any) -> User:
        # Validações e criação
        pass
    
    @staticmethod
    def email_from(dto: Any) -> str:
        return _get(dto, "email")
```

### 3. Mapper Pattern
```python
# mappers/user_mapper.py
class UserMapper:
    @staticmethod
    def to_public(user: User) -> UserResponse:
        # Conversão para resposta pública
        pass
    
    @staticmethod
    def to_display(user: User) -> UserDisplayResponse:
        # Conversão para exibição simples
        pass
```

### 4. Service Pattern
```python
# services/user_service.py
def create_user(dto: UserCreateRequest, repo) -> User:
    email = UserFactory.email_from(dto)
    if repo.exists_email(email):
        raise ValueError("Email já existe")
    
    user = UserFactory.make_user(dto)
    repo.add(user)
    return user
```

## 📊 Cronograma

- **Semana 1**: Reestruturação de pastas e implementação de Mappers
- **Semana 2**: Implementação de Factories e helpers
- **Semana 3**: Refatoração de Services e Repositories
- **Semana 4**: Atualização de API endpoints e testes

## ✅ Critérios de Sucesso

1. **Separação Clara**: Cada camada tem responsabilidade única
2. **Desacoplamento**: Camadas não conhecem detalhes internas
3. **Testabilidade**: Cada camada pode ser testada isoladamente
4. **Manutenibilidade**: Mudanças ficam contidas em suas camadas
5. **Escalabilidade**: Fácil adicionar novas funcionalidades

## 🚨 Pontos de Atenção

1. **Não quebrar funcionalidades existentes** durante refatoração
2. **Manter compatibilidade** com APIs existentes
3. **Implementar testes** para cada camada
4. **Documentar mudanças** para a equipe
5. **Fazer refatoração incremental** (não tudo de uma vez)
