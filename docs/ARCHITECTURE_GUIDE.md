Um Guia Completo para Estudantes
Introdução: Bem-vindo à Arquitetura IT Valley!
Meu querido estudante, seja bem-vindo ao mundo da Arquitetura Limpa IT Valley! Este documento
vai te ensinar uma das formas mais elegantes e organizadas de estruturar sistemas de software.
O que você vai aprender aqui:
Ao final desta jornada, você será capaz de construir sistemas robustos, testáveis e fáceis de manter.
Você dominará cada camada da nossa arquitetura e saberá exatamente onde colocar cada linha de
código.
🎯 ANOTE AQUI O QUE VOCÊ VAI DOMINAR:
1. API (Interface Externa):
Responsabilidade: ___________________________
O que pode fazer: ___________________________
O que NÃO pode fazer: ______________________
2. Service (Orquestrador):
Responsabilidade: ___________________________
O que pode fazer: ___________________________
O que NÃO pode fazer: ______________________
3. DTO/Schemas (Contratos):
Responsabilidade: ___________________________
O que pode fazer: ___________________________
O que NÃO pode fazer: ______________________
4. Domain (Coração do Sistema):
Responsabilidade: ___________________________
O que pode fazer: ___________________________
O que NÃO pode fazer: ______________________
5. Factory (Fábrica):
Responsabilidade: ___________________________
O que pode fazer: ___________________________
O que NÃO pode fazer: ______________________
6. Repository (Persistência):
Responsabilidade: ___________________________
O que pode fazer: ___________________________
O que NÃO pode fazer: ______________________
📝 Suas Anotações Importantes:
Dicas de Estudo:
Leia cada seção com calma, meu querido
Anote dúvidas e volte depois
Pratique os exemplos no seu computador
Não tenha pressa - arquitetura se aprende devagar
Agora vamos começar nossa jornada! 🚀
Sumário
1. Por que Arquitetura Importa?
2. O Conceito de Camadas
3. O Problema do Acoplamento
4. A Solução: Desacoplamento
5. Nossa Arquitetura IT Valley
6. As Camadas em Detalhes
7. O Que Pode e Não Pode em Cada Camada
8. A Árvore da Nossa Arquitetura
9. Exemplo Prático: Cliente
10. Fluxo Completo na Prática
11. Erros Comuns e Como Evitar
1. Por que Arquitetura Importa?
Meu querido, imagine que você está construindo uma casa. Você pode simplesmente empilhar tijolos
sem pensar, ou pode fazer um projeto arquitetônico primeiro. Qual das duas vai resultar numa casa
mais sólida e bonita?
No desenvolvimento de software, é a mesma coisa. Sem uma arquitetura bem definida, seu código
vira uma bagunça que ninguém consegue entender ou modificar.
Problemas de código sem arquitetura:
Quando você muda uma coisa, quebra três outras
É impossível testar as funcionalidades isoladamente
Novos desenvolvedores demoram semanas para entender o código
Bugs aparecem em lugares inesperados
Adicionar novas funcionalidades vira um pesadelo
Com uma boa arquitetura:
Mudanças ficam isoladas e controladas
Cada parte pode ser testada independentemente
O código fica fácil de entender e modificar
Bugs ficam contidos em suas respectivas camadas
Novas funcionalidades são simples de adicionar
2. O Conceito de Camadas
Pense numa empresa bem organizada, meu querido. Você tem diferentes departamentos:
Atendimento ao Cliente: Fala com o público
Vendas: Processa pedidos
Estoque: Gerencia produtos
Contabilidade: Cuida do dinheiro
Cada departamento tem sua responsabilidade específica e se comunica com os outros de forma
organizada.
No software, fazemos igual:
Benefícios das Camadas:
Organização: Cada coisa no seu lugar
Responsabilidade clara: Cada camada tem um papel específico
Facilita manutenção: Mudou algo na API? Só mexe na camada API
Testabilidade: Testa cada camada separadamente
3. O Problema do Acoplamento
Acoplamento é quando as coisas estão "grudadas" umas nas outras. Como aqueles fones de ouvido
que sempre enroscam no bolso!
Exemplo de código acoplado (RUIM):
┌─────────────────┐
│ Camada API │ ← Fala com o mundo exterior (como Atendimento)
├─────────────────┤
│ Camada Service │ ← Processa regras de negócio (como Vendas)
├─────────────────┤
│ Camada Domain │ ← Guarda as regras importantes (como Políticas da Empresa)
├─────────────────┤
│ Camada Repository│ ← Salva e busca dados (como Arquivo)
└─────────────────┘
python
Problemas desse código:
API conhece detalhes do banco de dados
Se mudar a tabela, quebra a API
Impossível testar sem banco real
Regras de negócio espalhadas por todo lugar
Se mudar validação, tem que mexer na API
4. A Solução: Desacoplamento
Desacoplamento é separar as responsabilidades e fazer cada parte conversar através de "contratos"
bem definidos.
Exemplo desacoplado (BOM):
# API fazendo tudo misturado - PÉSSIMO!
@app.post("/clientes")
def criar_cliente(request):
 # API acessando banco direto (acoplado!)
 if db.query("SELECT * FROM clientes WHERE email = ?", request.email):
 return {"erro": "Email já existe"}

 # API fazendo validação (responsabilidade errada!)
 if len(request.nome) < 2:
 return {"erro": "Nome muito curto"}

 # API montando SQL (muito acoplado!)
 db.execute("""
 INSERT INTO clientes (nome, email, status)
 VALUES (?, ?, 'ativo')
 """, request.nome, request.email)

 return {"sucesso": True}
python
Vantagens:
API não conhece banco de dados
Service não conhece detalhes de persistência
Cada parte pode ser testada isoladamente
Mudanças ficam contidas
5. Nossa Arquitetura IT Valley
Agora vou te mostrar nossa arquitetura completa, meu querido. É como um prédio bem organizado:
# API só coordena
@app.post("/clientes")
def criar_cliente(request):
 try:
 cliente = cliente_service.criar(request, repo)
 return mapper.to_response(cliente)
 except ValueError as e:
 return {"erro": str(e)}
# Service cuida das regras de negócio
def criar(request, repo):
 if repo.existe_email(request.email):
 raise ValueError("Email já existe")

 cliente = factory.criar_cliente(request)
 repo.salvar(cliente)
 return cliente
# Repository cuida do banco
def salvar(cliente):
 self.db.execute("INSERT INTO...", cliente.nome, cliente.email)
Fluxo de dados (de cima para baixo):
1. API recebe requisição HTTP
2. Schemas validam dados de entrada
3. Service orquestra o processo
4. Factory cria objetos do domínio
5. Domain aplica regras de negócio
6. Repository salva no banco
Fluxo de resposta (de baixo para cima):
1. Repository retorna dados
2. Domain processa regras
3. Service coordena retorno
4. Mapper converte para resposta
5. API retorna HTTP
┌─────────────────────────────────┐
│ 🌐 API │ ← Porta de entrada (térreo)
│ (FastAPI) │
├─────────────────────────────────┤
│ 📋 Schemas │ ← Contratos de entrada/saída
│ (Pydantic) │
├─────────────────────────────────┤
│ 🔄 Mappers │ ← Tradutores de dados
├─────────────────────────────────┤
│ ⚙️ Services │ ← Orquestrador (1º andar)
├─────────────────────────────────┤
│ 🏭 Factory │ ← Fábrica de objetos
├─────────────────────────────────┤
│ 🏛️ Domain │ ← Coração do sistema (2º andar)
│ (Entities) │
├─────────────────────────────────┤
│ 💾 Repository │ ← Guarda dados (subsolo)
│ (SQLAlchemy) │
├─────────────────────────────────┤
│ 🤖 AI Integration │ ← Inteligência artificial
└─────────────────────────────────┘
6. As Camadas em Detalhes
Vou explicar cada camada como se você fosse trabalhar nela amanhã, meu querido.
🌐 Camada API (Interface Externa)
Responsabilidade: Ser a "porta de entrada" do sistema. Como um recepcionista educado.
O que faz:
Recebe requisições HTTP (GET, POST, PUT, DELETE)
Valida se os dados estão no formato correto
Chama o Service apropriado
Retorna resposta HTTP formatada
Trata erros de forma amigável
Analogia: É o atendente da loja que recebe o cliente, entende o que ele quer, chama o vendedor
certo e entrega o produto.
📋 Camada Schemas (Contratos)
Responsabilidade: Definir "contratos" de entrada e saída. Como um formulário bem estruturado.
O que faz:
Define formato dos dados de entrada (Request)
Define formato dos dados de saída (Response)
Valida tipos, tamanhos, formatos
Documenta automaticamente a API
Analogia: São os formulários padronizados que o cliente preenche e os recibos formatados que ele
recebe.
python
@router.post("/clientes", response_model=ClienteResponse)
def criar_cliente(dto: ClienteCreateRequest, repo=Depends(repo_dep)):
 # 1. Recebeu dados (dto)
 # 2. Chama service
 cliente = service.criar_cliente(dto, repo)
 # 3. Converte resposta
 return mapper.to_public(cliente)
🔄 Camada Mappers (Tradutores)
Responsabilidade: Traduzir entre diferentes formatos de dados.
O que faz:
Converte Entity (domínio) para Response (API)
Permite diferentes "visões" dos mesmos dados
Protege dados internos de vazarem para fora
Analogia: É o tradutor que converte a linguagem técnica interna para a linguagem que o cliente
entende.
python
class ClienteCreateRequest(BaseModel):
 nome: str = Field(min_length=2, max_length=100)
 email: EmailStr
 telefone: Optional[str] = None
class ClienteResponse(BaseModel):
 id: str
 nome: str
 email: str
 status: str
python
⚙️ Camada Service (Orquestrador)
Responsabilidade: Coordenar casos de uso complexos. É o "gerente" que organiza tudo.
O que faz:
Orquestra fluxos de negócio
Coordena entre diferentes partes
Valida regras que dependem de dados externos
Controla transações
Analogia: É o gerente que coordena: "Primeiro consulta estoque, depois calcula desconto, se tudo ok,
registra venda".
class ClienteMapper:
 @staticmethod
 def to_public(cliente: Cliente) -> ClienteResponse:
 return ClienteResponse(
 id=cliente.id,
 nome=cliente.nome,
 email=cliente.email,
 status=cliente.status
 )
 @staticmethod
 def to_display(cliente: Cliente) -> ClienteDisplayResponse:
 return ClienteDisplayResponse(
 nome=cliente.nome,
 cargo=cliente.cargo # Só nome e cargo para tela simples
 )
python
🏭 Camada Factory (Fábrica)
Responsabilidade: Criar objetos do domínio de forma consistente.
O que faz:
Única porta de entrada para criar entidades
Centraliza validações de criação
Converte dados externos para objetos internos
Fornece helpers para Service extrair dados
Analogia: É a fábrica que monta carros. Você dá as especificações e ela entrega o carro pronto e
testado.
def criar_cliente(dto: ClienteCreateRequest, repo) -> Cliente:
 # 1. Validações que dependem do repositório
 email = email_from(dto)
 if repo.existe_email(email):
 raise ValueError("Email já existe")

 # 2. Cria entidade via Factory
 cliente = criar_cliente(dto)

 # 3. Persiste
 repo.add(cliente)

 return cliente
python
🏛️ Camada Domain (Coração)
Responsabilidade: Guardar as regras de negócio mais importantes. É a "alma" do sistema.
O que faz:
Define entidades (Cliente, Produto, Pedido)
Implementa comportamentos importantes
Garante integridade dos dados
Aplica regras de negócio puras
Analogia: São as regras fundamentais da empresa que nunca mudam, como "cliente deve ter nome"
ou "preço não pode ser negativo".
class ClienteFactory:
 @staticmethod
 def make_client(dto: Any) -> Cliente:
 nome = _get(dto, "nome")
 email = _get(dto, "email")

 # Validações
 if not nome or len(nome.strip()) < 2:
 raise ValueError("Nome muito curto")

 # Cria entidade completa
 return Cliente(
 id=uuid4().hex,
 nome=nome.strip(),
 email=email.strip(),
 status="ativo",
 created_at=datetime.utcnow()
 )
 @staticmethod
 def email_from(dto: Any) -> str:
 return _get(dto, "email") # Helper para Service
python
💾 Camada Repository (Armazenamento)
Responsabilidade: Guardar e buscar dados. É o "arquivo" do sistema.
O que faz:
Salva entidades no banco de dados
Busca entidades por diferentes critérios
Converte entre Entity (domínio) e Model (banco)
Isola detalhes do banco de dados
Analogia: É o arquivista que sabe exatamente onde guardar cada documento e como encontrá-lo
depois.
@dataclass
class Cliente:
 id: str
 nome: str
 email: str
 status: str = "ativo"

 def ativar(self) -> None:
 if self.status == "banido":
 raise ValueError("Cliente banido não pode ser ativado")
 self.status = "ativo"

 def desativar(self) -> None:
 self.status = "inativo"

 def aplicar_atualizacao_from_any(self, data: Any) -> None:
 # Aplica mudanças de qualquer fonte de dados
 novo_nome = _get(data, "nome")
 if novo_nome and len(novo_nome.strip()) >= 2:
 self.nome = novo_nome.strip()
python
🤖 Camada AI Integration (Inteligência)
Responsabilidade: Integrar com serviços de IA externos.
O que faz:
Define contratos para chamadas de IA
Implementa adapters para diferentes provedores
Processa resultados de IA
Mantém isolamento de IA do resto do sistema
Analogia: É o consultor especializado que você chama quando precisa de uma análise específica.
class ClienteRepository:
 def add(self, cliente: Cliente) -> None:
 model = self._to_model(cliente)
 self.session.add(model)
 self.session.commit()

 def get_by_email(self, email: str) -> Optional[Cliente]:
 model = self.session.query(ClienteModel).filter_by(email=email).first()
 return self._to_entity(model) if model else None

 def _to_entity(self, model: ClienteModel) -> Cliente:
 # Converte banco → domínio
 return Cliente(
 id=model.id,
 nome=model.nome,
 email=model.email,
 status=model.status
 )

 def _to_model(self, entity: Cliente) -> ClienteModel:
 # Converte domínio → banco
 return ClienteModel(
 id=entity.id,
 nome=entity.nome,
 email=entity.email,
 status=entity.status
 )
python
7. O Que Pode e Não Pode em Cada Camada
Agora vou te dar as regras claras, meu querido. É como um código de trânsito - precisa seguir para
funcionar.
🌐 API - PODE e NÃO PODE
✅ PODE:
Receber requisições HTTP
Validar formato básico (Pydantic faz isso)
Chamar Services
Usar Mappers para converter Entity → Response
Tratar exceções e retornar erros HTTP amigáveis
Configurar dependency injection simples
❌ NÃO PODE:
Acessar banco de dados diretamente
Implementar regras de negócio
Conhecer detalhes de como Entity funciona
Fazer cálculos complexos
Acessar campos do DTO diretamente (usar helpers)
Instanciar conexões de banco
class ClienteAIClient:
 def analisar_perfil(self, payload: ClienteAIPayload) -> ClienteAIResponse:
 # Chama serviço de IA externo
 response = self.ai_service.analyze(payload)
 return ClienteAIResponse(
 score_engajamento=response.score,
 categoria=response.category
 )
python
📋 Schemas - PODE e NÃO PODE
✅ PODE:
Definir estruturas de Request e Response
Validar tipos, tamanhos, formatos
Usar Field() para documentação
Ter validations automáticas do Pydantic
Definir diferentes DTOs para contextos diferentes
❌ NÃO PODE:
Implementar lógica de negócio
Acessar banco de dados
Fazer cálculos complexos
Depender de outras camadas (exceto tipos básicos)
# ✅ CORRETO
@router.post("/clientes")
def criar(dto: ClienteCreateRequest, repo=Depends(repo_dep)):
 cliente = service.criar_cliente(dto, repo)
 return mapper.to_public(cliente)
# ❌ ERRADO
@router.post("/clientes")
def criar(dto: ClienteCreateRequest):
 # ERRO: API acessando banco
 if db.query("SELECT * FROM clientes WHERE email = ?", dto.email):
 return {"erro": "Email existe"}

 # ERRO: API fazendo validação
 if len(dto.nome) < 2:
 return {"erro": "Nome curto"}
python
⚙️ Service - PODE e NÃO PODE
✅ PODE:
Orquestrar casos de uso
Chamar Factory para criar entidades
Usar Repository para persistir/buscar
Coordenar entre diferentes partes
Validar regras que dependem de dados externos
Usar helpers da Factory para extrair dados
❌ NÃO PODE:
Acessar campos do DTO diretamente (dto.nome)
Conhecer detalhes de banco de dados
Instanciar entidades diretamente
Implementar validações que a Entity pode fazer
Retornar DTOs (retorna Entities)
# ✅ CORRETO
class ClienteCreateRequest(BaseModel):
 nome: str = Field(min_length=2, max_length=100)
 email: EmailStr
 telefone: Optional[str] = None
# ❌ ERRADO
class ClienteCreateRequest(BaseModel):
 nome: str
 email: str

 def validar_email_unico(self): # ERRO: regra de negócio
 # Não pode acessar banco aqui!
 pass
python
🏭 Factory - PODE e NÃO PODE

✅ PODE:
Ser única porta de criação de entidades
Fazer validações de criação
Extrair dados de DTOs usando _get()
Fornecer helpers para Service (email_from, id_from)
Converter tipos de dados
Gerar IDs únicos

❌ NÃO PODE:
Acessar banco de dados
Depender de Repository
Fazer validações que precisam de dados externos
Retornar entidades parciais
Ter múltiplas formas de criar a mesma entidade

# ✅ CORRETO
def criar_cliente(dto: ClienteCreateRequest, repo) -> Cliente:
 email = email_from(dto) # Helper da Factory
 if repo.existe_email(email):
 raise ValueError("Email já existe")

 cliente = criar_cliente(dto) # Factory cria
 repo.add(cliente)
 return cliente

# ❌ ERRADO
def criar_cliente(dto: ClienteCreateRequest, repo) -> Cliente:
 if repo.existe_email(dto.email): # ERRO: acessou dto.email
 raise ValueError("Email já existe")

 # ERRO: criou entidade diretamente
 cliente = Cliente(nome=dto.nome, email=dto.email)
 repo.add(cliente)
 return cliente
python

🏛️ Domain - PODE e NÃO PODE

✅ PODE:
Definir entidades como dataclass
Implementar comportamentos (ativar, desativar)
Validar invariantes da entidade
Aplicar regras de negócio puras
Usar método aplicar_atualizacao_from_any()
Ter propriedades calculadas

❌ NÃO PODE:
Importar Pydantic, FastAPI, SQLAlchemy
Acessar banco de dados
Ter @staticmethod criar() (só Factory cria)
Depender de camadas externas
Fazer validações que precisam de dados externos

# ✅ CORRETO
def criar_cliente(dto: Any) -> Cliente:
 nome = _get(dto, "nome")
 email = _get(dto, "email")

 if not nome or len(nome.strip()) < 2:
 raise ValueError("Nome muito curto")

 return Cliente(
 id=uuid4().hex,
 nome=nome.strip(),
 email=email.strip(),
 status="ativo"
 )
# ❌ ERRADO
def criar_cliente(dto: Any, repo) -> Cliente: # ERRO: depende de repo
 if repo.existe_email(dto.email): # ERRO: validação externa
 raise ValueError("Email existe")

 return Cliente(nome=dto.nome) # ERRO: entidade incompleta
💾 Repository - PODE e NÃO PODE
✅ PODE:
Salvar/buscar/atualizar entidades
Converter Entity ↔ Model (mapeamentos privados)
Usar SQLAlchemy, MongoDB, etc.
Fazer queries complexas quando necessário
Implementar métodos como get_by_email, list, etc.
❌ NÃO PODE:
python
# ✅ CORRETO
@dataclass
class Cliente:
 id: str
 nome: str
 email: str
 status: str = "ativo"

 def ativar(self) -> None:
 self.status = "ativo"
 self.updated_at = datetime.utcnow()

 def aplicar_atualizacao_from_any(self, data: Any) -> None:
 novo_nome = _get(data, "nome")
 if novo_nome and len(novo_nome.strip()) >= 2:
 self.nome = novo_nome.strip()
# ❌ ERRADO
@dataclass
class Cliente:
 nome: str

 @staticmethod # ERRO: só Factory cria
 def criar(nome: str):
 return Cliente(nome=nome)

 def validar_email_unico(self, repo): # ERRO: depende de repo
 return repo.existe_email(self.email)
Implementar regras de negócio
Validar dados (isso é do Domain)
Conhecer detalhes de API ou DTOs
Fazer cálculos de negócio
Expor detalhes do banco para outras camadas
8. A Árvore da Nossa Arquitetura
Aqui está como você vai organizar seus arquivos, meu querido:
python
# ✅ CORRETO
class ClienteRepository:
 def add(self, cliente: Cliente) -> None:
 model = self._to_model(cliente)
 self.session.add(model)
 self.session.commit()

 def _to_model(self, entity: Cliente) -> ClienteModel:
 return ClienteModel(
 id=entity.id,
 nome=entity.nome,
 email=entity.email
 )
# ❌ ERRADO
class ClienteRepository:
 def add(self, cliente: Cliente) -> None:
 # ERRO: validação (isso é do Domain)
 if len(cliente.nome) < 2:
 raise ValueError("Nome muito curto")

 # ERRO: regra de negócio
 if cliente.idade < 18:
 cliente.status = "menor_idade"
projeto/
├── app/
│ ├── __init__.py
│ ├── main.py # FastAPI app principal
│ │
│ ├── api/ # 🌐 Camada API
│ │ ├── __init__.py
│ │ ├── clientes_api.py # Endpoints de cliente
│ │ ├── funcionarios_api.py # Endpoints de funcionário
│ │ └── produtos_api.py # Endpoints de produto
│ │
│ ├── schemas/ # 📋 Contratos (DTOs)
│ │ ├── __init__.py
│ │ ├── clientes/
│ │ │ ├── __init__.py
│ │ │ ├── requests.py # ClienteCreateRequest, etc.
│ │ │ └── responses.py # ClienteResponse, etc.
│ │ ├── funcionarios/
│ │ │ ├── requests.py
│ │ │ └── responses.py
│ │ └── produtos/
│ │ ├── requests.py
│ │ └── responses.py
│ │
│ ├── mappers/ # 🔄 Tradutores
│ │ ├── __init__.py
│ │ ├── cliente_mapper.py # to_public(), to_display()
│ │ ├── funcionario_mapper.py
│ │ └── produto_mapper.py
│ │
│ ├── services/ # ⚙️ Orquestradores
│ │ ├── __init__.py
│ │ ├── cliente_service.py # criar_cliente_service(), etc.
│ │ ├── funcionario_service.py
│ │ └── produto_service.py
│ │
│ ├── domain/ # 🏛️ Coração do Sistema
│ │ ├── __init__.py
│ │ ├── clientes/
│ │ │ ├── __init__.py
│ │ │ ├── cliente_entity.py # Classe Cliente
│ │ │ └── cliente_factory.py # criar_cliente()
│ │ ├── funcionarios/
│ │ │ ├── funcionario_entity.py
│ │ │ └── funcionario_factory.py
│ │ └── produtos/
│ │ ├── produto_entity.py
│ │ └── produto_factory.py
│ │
│ ├── data/ # 💾 Persistência
│ │ ├── __init__.py
│ │ ├── models/ # Models do SQLAlchemy
│ │ │ ├── __init__.py
│ │ │ ├── cliente_model.py # ClienteModel (SQLAlchemy)
│ │ │ ├── funcionario_model.py
│ │ │ └── produto_model.py
│ │ └── repositories/ # Repositórios
│ │ ├── __init__.py
│ │ ├── cliente_repository.py # ClienteRepository
│ │ ├── funcionario_repository.py
│ │ └── produto_repository.py
│ │
│ ├── integrations/ # 🤖 Integrações Externas
│ │ ├── __init__.py
│ │ └── ai/
│ │ ├── __init__.py
│ │ ├── clientes/
│ │ │ ├── __init__.py
│ │ │ ├── payloads.py # DTOs para IA
│ │ │ └── client.py # Cliente IA
│ │ ├── funcionarios/
│ │ │ ├── payloads.py
│ │ │ └── client.py
│ │ └── produtos/
│ │ ├── payloads.py
│ │ └── client.py
│ │
│ └── config/ # ⚙️ Configurações
│ ├── __init__.py
│ ├── database.py # Configuração do banco
│ └── settings.py # Configurações gerais
│
├── tests/ # 🧪 Testes
│ ├── unit/ # Testes unitários
│ │ ├── test_cliente_entity.py
│ │ ├── test_cliente_factory.py
│ │ └── test_cliente_service.py

Explicação dos Diretórios:
📁 api/: Todos os endpoints da sua API. Um arquivo por entidade.
📁 schemas/: Contratos de entrada e saída. Separados por entidade, com requests e responses.
📁 mappers/: Conversores de Entity para Response. Um arquivo por entidade.
📁 services/: Orquestradores de casos de uso. Coordenam o fluxo sem implementar regras.
📁 domain/: O coração do sistema. Entidades + Factories. Separado por contexto de negócio.
📁 data/: Tudo relacionado a persistência. Models (SQLAlchemy) e Repositories.
📁 integrations/: Integrações com sistemas externos (IA, APIs de terceiros).
📁 config/: Configurações de banco, variáveis de ambiente, etc.
