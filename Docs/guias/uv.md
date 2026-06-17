# Guia — UV (gerenciador de dependências Python)

O **UV** é a ferramenta que o grupo usa para instalar bibliotecas Python, criar o ambiente virtual (`.venv`) e rodar scripts — sem `pip install` manual solto na máquina.

Site oficial: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)

---

## Por que usamos UV neste repositório?

| Motivo | Detalhe |
|--------|---------|
| Velocidade | Resolve e instala pacotes bem mais rápido que o `pip` tradicional |
| Reprodutibilidade | O arquivo `uv.lock` fixa versões exatas para todo o grupo |
| Simplicidade | `uv run` executa scripts sem precisar `source .venv/bin/activate` |
| Padrão do trabalho | Alinhado ao template e às práticas de Engenharia de Dados |

**Não usamos Poetry** neste repositório.

---

## Onde o UV aparece no projeto

```
projeto-ed-final/
├── pyproject.toml    # dependências declaradas (nome do projeto, pacotes)
├── uv.lock           # versões travadas (commitar no git)
├── .venv/            # ambiente local (não vai pro git — está no .gitignore)
└── scripts/
    └── seed_database.py   # exemplo de script rodado com uv run
```

Dependências atuais (issue #7):

- `faker` — dados fictícios do banco
- `sqlalchemy` + `psycopg2-binary` — conexão com PostgreSQL

---

## Instalação (WSL / Ubuntu)

### 1. Pipx (recomendado)

O UV é instalado globalmente via **pipx**, isolado do sistema:

```bash
sudo apt update
sudo apt install -y pipx
pipx ensurepath
source ~/.bashrc
```

### 2. UV

```bash
pipx install uv
uv --version
```

Saída esperada: algo como `uv 0.x.x`.

---

## Comandos do dia a dia

Todos os exemplos assumem que você está na raiz do repositório:

```bash
cd /mnt/c/projeto-ed-final
```

### `uv sync` — instalar dependências

Lê `pyproject.toml` + `uv.lock` e cria/atualiza o `.venv`:

```bash
uv sync
```

Rode sempre que:

- clonar o repositório pela primeira vez;
- alguém do grupo adicionar pacote novo e atualizar o `uv.lock`;
- trocar de branch com mudanças em dependências.

### `uv run` — executar script no venv

Não precisa ativar o `.venv` manualmente:

```bash
uv run python scripts/seed_database.py
```

Outros exemplos:

```bash
uv run python --version
uv run ruff check scripts/
```

### `uv add` — adicionar pacote (quem desenvolve)

```bash
uv add nome-do-pacote
```

Isso atualiza `pyproject.toml` e `uv.lock`. **Commite os dois arquivos** no PR.

Pacote só para desenvolvimento (ex.: linter):

```bash
uv add --dev pytest
```

### `uv venv` + `activate` (opcional)

Se preferir o fluxo clássico:

```bash
uv venv
source .venv/bin/activate
python scripts/seed_database.py
deactivate
```

No dia a dia, `uv run` costuma ser mais prático.

---

## Fluxo completo — seed do Postgres (issue #7)

```bash
cd /mnt/c/projeto-ed-final
source scripts/wsl-env.sh

# 1. Postgres no Docker
dcompose up -d postgres

# 2. Dependências Python
uv sync

# 3. Popular o banco
uv run python scripts/seed_database.py

# 4. Conferir
bash scripts/verify-postgres.sh
```

Variável opcional (já definida no `wsl-env.sh`):

```bash
export DATABASE_URL="postgresql://sparkeats:sparkeats_dev@localhost:5433/sparkeats"
```

---

## Problemas comuns

### Aviso `Failed to hardlink files`

Ao rodar `uv sync` em pasta no Windows (`/mnt/c/...`), pode aparecer:

```text
warning: Failed to hardlink files; falling back to full copy.
```

É **normal** — o UV copia os arquivos em vez de usar hardlink. Pode ignorar ou suprimir:

```bash
export UV_LINK_MODE=copy
uv sync
```

### `uv: command not found`

```bash
pipx ensurepath
source ~/.bashrc
# ou feche e abra o terminal WSL
```

### Pacote instalado mas script não acha

Quase sempre falta `uv sync` ou você rodou `python` do sistema em vez de:

```bash
uv run python scripts/seu_script.py
```

### Versão do Python

O projeto exige **Python 3.12+** (`requires-python` no `pyproject.toml`):

```bash
python3 --version
```

---

## Referência rápida

| Comando | O que faz |
|---------|-----------|
| `uv sync` | Instala/atualiza `.venv` conforme lockfile |
| `uv run <cmd>` | Roda comando dentro do venv |
| `uv add <pkg>` | Adiciona dependência e atualiza lock |
| `uv lock` | Regenera `uv.lock` sem instalar |
| `uv pip list` | Lista pacotes do ambiente |

---

## Próximos guias (sugestões)

- Docker + `dcompose` no WSL
- PostgreSQL / DBeaver
- Git: branch → PR → review
