# Convenções

Padrões adotados no projeto para manter consistência no código e no histórico do Git.

## Commits

Seguimos o padrão [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
<tipo>(<escopo>): <descrição curta>
```

| Tipo | Quando usar |
|------|-------------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `refactor` | Refatoração sem mudança de comportamento |
| `chore` | Tarefas de manutenção (deps, config) |
| `test` | Adição ou correção de testes |

**Exemplos:**

```
feat(pipeline): adiciona DAG da camada silver
fix(seed): corrige distribuição de datas no seed_database
docs(mkdocs): atualiza página do modelo dimensional
chore(deps): atualiza pyspark para 3.4.2
```

## Branches

| Padrão | Uso |
|--------|-----|
| `feat/<descricao>` | Nova funcionalidade |
| `fix/<descricao>` | Correção |
| `docs/<descricao>` | Documentação |
| `refactor/<descricao>` | Refatoração |

**Exemplos:**

```bash
git checkout -b feat/dag-silver
git checkout -b docs/update-readme
git checkout -b fix/seed-date-distribution
```

## Código Python

- Formatação: **ruff**
- Python: **3.12+**
- Gerenciador: **uv**

```bash
uv run ruff check .
uv run ruff format .
```

## Issues

Toda tarefa deve ter uma issue correspondente no GitHub antes de ser iniciada. Use o número da issue no título do PR.