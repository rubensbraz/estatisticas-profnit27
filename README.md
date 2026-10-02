# PROFNIT 2027 - Exame Nacional de Acesso (ENA27) - Análise Estatística & Gerador de PDF

Projeto em Python gerenciado com `uv` para extração de dados, análise estatística descritiva, geração de gráficos e compilação de relatórios executivos em PDF sobre o Resultado Preliminar do Exame Nacional de Acesso ao PROFNIT 2027 (`data/ENA27-Resultado-Preliminar-Prova-Nacional.pdf`).

O código-fonte em Python é estruturado de forma limpa, com docstrings e type hints detalhados.

---

## 📄 Visualizar o Relatório em PDF

👉 **[Abrir o Relatório Executivo em PDF](https://github.com/rubensbraz/estatisticas-profnit27/blob/main/output/PROFNIT_2027_Preliminary_Results_Report.pdf)**

O GitHub exibe o PDF diretamente no navegador ao abrir o link acima — não é necessário clonar o repositório ou navegar pela pasta `output/`.

---

## 🚀 Principais Funcionalidades

- **Extração de Dados em PDF**: Leitura e parsing de nomes, CPFs mascarados, presenças e notas de 1.845 candidatos ao longo de 57 páginas.
- **Estatísticas Completas**:
  - **Frequência de Presença**: Total de inscritos, presentes, ausentes e respectivas porcentagens.
  - **Métricas Descritivas**: Média, mediana, moda, desvio padrão, variância, nota mínima, nota máxima, percentis (Q1, Q3) e intervalo interquartil (IQR).
  - **Cortes de Nota**: Distribuição de notas (0 a 20), percentuais acumulados e volume de candidatos de alto desempenho.
  - **Demografia Geográfica**: Agrupamento por código de estado do CPF (9º dígito), detalhando volume de candidatos e média de acertos por região.
- **Gráficos em Alta Resolução**: Visualizações geradas com Matplotlib e Seaborn (histograma de acertos, curva de porcentagem acumulada, volume por região e média por região).
- **Relatório Executivo em PDF**: Documento profissional em PDF estruturado com ReportLab (3 páginas), incluindo cards KPI, tabelas formatadas, numeração dinâmica de páginas ("Página X de Y") e gráficos integrados.

---

## 🛠️ Requisitos e Gerenciamento de Ambiente

O projeto utiliza o [`uv`](https://github.com/astral-sh/uv) para gerenciamento rápido e reprodutível do ambiente Python.

### Instalação das Dependências

Para sincronizar o ambiente e instalar dependências:

```bash
uv sync
```

---

## 💻 Como Usar

### Executar Pipeline Completo

Para rodar a análise e gerar o relatório em PDF com as configurações padrão:

```bash
uv run profnit-stats
```

Ou diretamente via módulo Python:

```bash
uv run python -m src.main
```

### Opções Personalizadas

É possível especificar caminhos customizados de entrada e saída:

```bash
uv run profnit-stats -i data/ENA27-Resultado-Preliminar-Prova-Nacional.pdf -o output/Relatorio.pdf -c output/charts
```

---

## 📁 Arquivos Gerados

1. **Relatório em PDF**: [`output/PROFNIT_2027_Preliminary_Results_Report.pdf`](https://github.com/rubensbraz/estatisticas-profnit27/blob/main/output/PROFNIT_2027_Preliminary_Results_Report.pdf)
2. **Gráficos PNG**:
   - [`output/charts/score_distribution.png`](https://github.com/rubensbraz/estatisticas-profnit27/blob/main/output/charts/score_distribution.png)
   - [`output/charts/cumulative_distribution.png`](https://github.com/rubensbraz/estatisticas-profnit27/blob/main/output/charts/cumulative_distribution.png)
   - [`output/charts/regional_volume.png`](https://github.com/rubensbraz/estatisticas-profnit27/blob/main/output/charts/regional_volume.png)
   - [`output/charts/regional_means.png`](https://github.com/rubensbraz/estatisticas-profnit27/blob/main/output/charts/regional_means.png)

---

## 🏗️ Estrutura do Projeto

```text
estatisticas-profnit27/
├── data/
│   └── ENA27-Resultado-Preliminar-Prova-Nacional.pdf
├── output/
│   ├── PROFNIT_2027_Preliminary_Results_Report.pdf
│   └── charts/
├── src/
│   ├── __init__.py
│   ├── parser.py          # Módulo de extração do PDF
│   ├── analyzer.py        # Módulo de estatística e mapeamento de CPF
│   ├── charts.py          # Módulo gerador de gráficos (Matplotlib/Seaborn)
│   ├── pdf_generator.py   # Módulo construtor do PDF (ReportLab Platypus)
│   └── main.py            # Ponto de entrada CLI
├── pyproject.toml
└── README.md
```
