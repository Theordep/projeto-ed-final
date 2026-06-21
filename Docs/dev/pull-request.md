# Fluxo de Pull Request

Todo código entra na `main` obrigatoriamente via Pull Request. Push direto está bloqueado.

## Passo a passo

### 1. Abra uma issue

Antes de começar qualquer trabalho, crie uma issue descrevendo o que será feito.

### 2. Crie uma branch

```bash
git checkout -b feat/nome-da-feature
```

### 3. Faça suas alterações e commit

```bash
git add .
git commit -m "feat(escopo): descrição curta"
```

Siga as [convenções de commit](convencoes.md).

### 4. Suba a branch

```bash
git push origin feat/nome-da-feature
```

### 5. Abra o Pull Request

Acesse o repositório no GitHub — o botão **"Compare & pull request"** aparece automaticamente.

Preencha:
- **Título**: siga o padrão Conventional Commits
- **Descrição**: o que foi feito e por quê
- **Closes #N**: referência à issue relacionada

### 6. Aguarde revisão

Pelo menos **1 aprovação** é necessária antes do merge. O autor do PR não pode aprovar o próprio PR.

### 7. Merge e limpeza

Após aprovado, faça o merge via GitHub. Delete a branch após o merge:

```bash
git checkout main
git pull origin main
git branch -d feat/nome-da-feature
```

## Checklist do PR

- [ ] Branch criada a partir da `main` atualizada
- [ ] Commits seguem o padrão Conventional Commits
- [ ] Issue referenciada no PR (`Closes #N`)
- [ ] Código testado localmente
- [ ] Documentação atualizada (se necessário)