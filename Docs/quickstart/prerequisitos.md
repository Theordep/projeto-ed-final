# Pré-requisitos

Ferramentas necessárias antes de instalar o projeto.

## Ferramentas obrigatórias

| Ferramenta | Versão | Link |
|------------|--------|------|
| Java (JDK) | **17** | [adoptium.net](https://adoptium.net/temurin/releases/?version=17) |
| Python | **3.12** | [python.org](https://www.python.org/downloads/) |
| uv | **latest** | [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| Docker Desktop | **latest** | [docker.com](https://www.docker.com/products/docker-desktop/) |

!!! warning "Java 17 obrigatório"
    O Apache Spark **não é compatível com Java 21+**. Use exclusivamente o JDK 17.

## Verificar instalações

```bash
java -version
python --version
uv --version
docker --version
docker compose version
```

## Configurar JAVA_HOME (Linux/WSL)

Adicione ao `~/.bashrc` ou `~/.zshrc`:

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

Recarregue o terminal:

```bash
source ~/.bashrc
```

Verifique:

```bash
echo $JAVA_HOME
```