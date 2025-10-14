# 📱 Connect-Cell Dashboard

Dashboard financeiro e operacional interativo para gestão de assistência técnica de celulares.

## 🚀 Funcionalidades

### 📊 Dashboard Principal
- **Métricas em Tempo Real**: KPIs financeiros com comparação mensal
- **Insights Automáticos**: Análises financeiras e operacionais geradas automaticamente
- **Gráficos Interativos**: Visualizações dinâmicas com Plotly
- **Análise Temporal**: Comparações mês a mês com indicadores de crescimento
- **Análise por Categoria**: Performance detalhada por tipo de serviço
- **Análise por Técnico**: Produtividade e receita individual
- **Exportação de Dados**: Download em CSV para análises externas

### 📋 Tabela de Serviços
- **KPIs Resumidos**: Visualização de métricas dos dados filtrados
- **Filtros Avançados**: Busca multi-campo por status, categoria, técnico e data
- **Edição Inline**: Modificação direta com validação
- **Feedback Visual**: Mensagens contextuais de resultados
- **Sincronização Automática**: Integração com Google Sheets

### ➕ Novo Serviço
- **Formulário Organizado**: Seções para Cliente, Serviço e Financeiro
- **Cálculos em Tempo Real**: Preview de Lucro Bruto, Comissão e Margem
- **Validações Robustas**: Verificação de campos obrigatórios e valores
- **Alertas Inteligentes**: Avisos de lucro negativo ou margem baixa
- **Dicas Contextuais**: Guia de preenchimento em cada campo

### 📅 Comparação Temporal
- **Análise entre Períodos**: Compare dois períodos customizáveis
- **Variação Percentual**: Métricas com crescimento/queda
- **Comparação por Categoria**: Performance detalhada de cada tipo de serviço
- **Comparação por Técnico**: Produtividade individual comparada
- **Tendência Mensal**: Gráfico de evolução com múltiplas métricas

### 🔬 Análise Avançada
- **Sistema de Alertas**: Detecção automática de situações críticas
- **Detecção de Anomalias**: Identificação de valores fora do padrão
- **Análise de Sazonalidade**: Padrões mensais de faturamento
- **Análise de Clientes**: Classificação RFM (Recência, Frequência, Monetário)
- **Previsão Simples**: Estimativa de faturamento para próximo mês

### 📚 Dicionário de Dados
- Documentação completa das colunas
- Exemplos e formatos de dados
- Guia de uso do sistema

## 🛠️ Tecnologias

- **Python 3.12+**
- **Streamlit** - Framework web
- **Pandas** - Manipulação de dados
- **Plotly** - Visualizações interativas
- **Google Sheets API** - Armazenamento de dados

## 📦 Instalação

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/Connect-Cell.git
cd Connect-Cell
```

### 2. Criar ambiente virtual
```bash
python3.12 -m venv .venv
source .venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Google Sheets

#### a) Criar Service Account
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie/selecione um projeto
3. Ative a **Google Sheets API**
4. Crie uma **Service Account**
5. Baixe o arquivo JSON de credenciais

#### b) Configurar secrets.toml
Crie o arquivo `.streamlit/secrets.toml` com as credenciais da Service Account e a URL da planilha.

#### c) Compartilhar planilha
Compartilhe sua planilha do Google Sheets com o email da Service Account (com permissão de Editor).

### 5. Executar o dashboard
```bash
streamlit run Dashboard.py
```

O dashboard abrirá automaticamente em `http://localhost:8501`

## 🏗️ Arquitetura

```
Connect-Cell/
├── Dashboard.py              # Dashboard principal refatorado
├── config.py                 # Configurações centralizadas
├── requirements.txt          # Dependências
├── pages/                    # Páginas adicionais
├── utils/                    # Utilitários e lógica de negócio
└── settings/                 # Configurações
```

## 🎨 Melhorias Implementadas

### Arquitetura
- ✅ Configuração centralizada com Enums
- ✅ Singleton pattern para conexão com Google Sheets
- ✅ Cache otimizado (1 hora TTL)
- ✅ Tratamento robusto de erros
- ✅ Logging estruturado
- ✅ Componentes reutilizáveis

### Design & UX
- ✅ CSS centralizado e reutilizável
- ✅ Tema consistente em todo o app
- ✅ Loading states visíveis
- ✅ Métricas com deltas e comparações
- ✅ Gráficos responsivos
- ✅ Hover tooltips melhorados

### Análises
- ✅ Insights automáticos financeiros
- ✅ Insights automáticos operacionais
- ✅ Comparações período a período
- ✅ Taxa de crescimento
- ✅ Detecção de anomalias
- ✅ Top performers por categoria
- ✅ KPIs calculados dinamicamente

### Features
- ✅ Exportação para CSV
- ✅ Botão de atualização de dados
- ✅ Filtros de data na sidebar
- ✅ Detalhes expandíveis por categoria
- ✅ Análise de margem de lucro
- ✅ Identificação de cliente mais valioso

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto está licenciado sob a licença MIT.
