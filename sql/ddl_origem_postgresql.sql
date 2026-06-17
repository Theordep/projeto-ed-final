-- =============================================================================
-- SparkEats — DDL Banco Origem (OLTP)
-- SGBD: PostgreSQL 16+
-- Database: sparkeats
-- Issue: https://github.com/Theordep/projeto-ed-final/issues/7
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Dimensões de apoio
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS categorias_restaurante (
    id_categoria   SERIAL PRIMARY KEY,
    nome           VARCHAR(80)  NOT NULL UNIQUE,
    descricao      VARCHAR(255),
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS zonas_entrega (
    id_zona        SERIAL PRIMARY KEY,
    nome_bairro    VARCHAR(100) NOT NULL,
    cidade         VARCHAR(100) NOT NULL,
    estado         CHAR(2) NOT NULL,
    regiao         VARCHAR(50) NOT NULL,
    taxa_entrega   DECIMAL(6, 2) NOT NULL DEFAULT 5.99,
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (nome_bairro, cidade, estado)
);

CREATE TABLE IF NOT EXISTS cupons (
    id_cupom       SERIAL PRIMARY KEY,
    codigo         VARCHAR(20)  NOT NULL UNIQUE,
    descricao      VARCHAR(255),
    percentual     DECIMAL(5, 2),
    valor_fixo     DECIMAL(10, 2),
    dt_inicio      DATE NOT NULL,
    dt_fim         DATE NOT NULL,
    ativo          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- Entidades principais
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS restaurantes (
    id_restaurante     SERIAL PRIMARY KEY,
    id_categoria       INT NOT NULL REFERENCES categorias_restaurante (id_categoria),
    id_zona            INT NOT NULL REFERENCES zonas_entrega (id_zona),
    nome_fantasia      VARCHAR(120) NOT NULL,
    razao_social       VARCHAR(180),
    cnpj               VARCHAR(18) UNIQUE,
    taxa_comissao      DECIMAL(5, 2) NOT NULL DEFAULT 15.00,
    status             VARCHAR(20) NOT NULL DEFAULT 'ATIVO'
        CHECK (status IN ('ATIVO', 'INATIVO', 'SUSPENSO')),
    created_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cardapio (
    id_item            SERIAL PRIMARY KEY,
    id_restaurante     INT NOT NULL REFERENCES restaurantes (id_restaurante),
    nome_item          VARCHAR(120) NOT NULL,
    descricao          VARCHAR(255),
    preco              DECIMAL(10, 2) NOT NULL CHECK (preco > 0),
    disponivel         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente         SERIAL PRIMARY KEY,
    nome               VARCHAR(150) NOT NULL,
    email              VARCHAR(180) NOT NULL,
    telefone           VARCHAR(20),
    cpf                VARCHAR(14) UNIQUE,
    data_inicio        DATE NOT NULL,
    data_fim           DATE,
    status_ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_clientes_email_ativo
    ON clientes (email) WHERE status_ativo = TRUE;

CREATE TABLE IF NOT EXISTS enderecos_cliente (
    id_endereco        SERIAL PRIMARY KEY,
    id_cliente         INT NOT NULL REFERENCES clientes (id_cliente),
    logradouro         VARCHAR(200) NOT NULL,
    numero             VARCHAR(10),
    bairro             VARCHAR(100) NOT NULL,
    cidade             VARCHAR(100) NOT NULL,
    estado             CHAR(2) NOT NULL,
    cep                VARCHAR(10),
    complemento        VARCHAR(100),
    principal          BOOLEAN NOT NULL DEFAULT FALSE,
    data_inicio        DATE NOT NULL,
    data_fim           DATE,
    status_ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS entregadores (
    id_entregador      SERIAL PRIMARY KEY,
    id_zona            INT NOT NULL REFERENCES zonas_entrega (id_zona),
    nome               VARCHAR(150) NOT NULL,
    cpf                VARCHAR(14) UNIQUE,
    telefone           VARCHAR(20),
    veiculo            VARCHAR(20) NOT NULL DEFAULT 'MOTO'
        CHECK (veiculo IN ('MOTO', 'BICICLETA', 'CARRO')),
    status             VARCHAR(20) NOT NULL DEFAULT 'ATIVO'
        CHECK (status IN ('ATIVO', 'INATIVO')),
    created_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMP NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- Transações (volume alto)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido          BIGSERIAL PRIMARY KEY,
    id_cliente         INT NOT NULL REFERENCES clientes (id_cliente),
    id_restaurante     INT NOT NULL REFERENCES restaurantes (id_restaurante),
    id_entregador      INT NOT NULL REFERENCES entregadores (id_entregador),
    id_cupom           INT REFERENCES cupons (id_cupom),
    data_hora_pedido   TIMESTAMP NOT NULL,
    data_hora_coleta   TIMESTAMP,
    data_hora_entrega  TIMESTAMP,
    status_pedido      VARCHAR(20) NOT NULL
        CHECK (status_pedido IN ('ENTREGUE', 'CANCELADO', 'EM_TRANSITO', 'PREPARANDO')),
    valor_itens        DECIMAL(10, 2) NOT NULL DEFAULT 0,
    taxa_entrega       DECIMAL(10, 2) NOT NULL DEFAULT 0,
    desconto           DECIMAL(10, 2) NOT NULL DEFAULT 0,
    valor_total        DECIMAL(10, 2) NOT NULL DEFAULT 0,
    tempo_entrega_min  INT,
    observacao         VARCHAR(255),
    created_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    id_item_pedido     BIGSERIAL PRIMARY KEY,
    id_pedido          BIGINT NOT NULL REFERENCES pedidos (id_pedido),
    id_item            INT NOT NULL REFERENCES cardapio (id_item),
    quantidade         INT NOT NULL DEFAULT 1 CHECK (quantidade > 0),
    preco_unitario     DECIMAL(10, 2) NOT NULL,
    subtotal           DECIMAL(10, 2) NOT NULL,
    created_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pagamentos (
    id_pagamento       BIGSERIAL PRIMARY KEY,
    id_pedido          BIGINT NOT NULL UNIQUE REFERENCES pedidos (id_pedido),
    forma_pagamento    VARCHAR(20) NOT NULL
        CHECK (forma_pagamento IN ('PIX', 'CARTAO', 'DINHEIRO')),
    status_pagamento   VARCHAR(20) NOT NULL DEFAULT 'APROVADO'
        CHECK (status_pagamento IN ('APROVADO', 'PENDENTE', 'ESTORNADO')),
    valor_pago         DECIMAL(10, 2) NOT NULL,
    dt_pagamento       TIMESTAMP NOT NULL,
    created_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS avaliacoes (
    id_avaliacao       BIGSERIAL PRIMARY KEY,
    id_pedido          BIGINT NOT NULL UNIQUE REFERENCES pedidos (id_pedido),
    nota_restaurante   DECIMAL(2, 1) CHECK (nota_restaurante BETWEEN 1 AND 5),
    nota_entrega       DECIMAL(2, 1) CHECK (nota_entrega BETWEEN 1 AND 5),
    nota_geral         DECIMAL(2, 1) CHECK (nota_geral BETWEEN 1 AND 5),
    comentario         VARCHAR(500),
    dt_avaliacao       TIMESTAMP NOT NULL,
    created_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMP NOT NULL DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- Índices (extração incremental e consultas operacionais)
-- -----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_pedidos_data_hora_pedido ON pedidos (data_hora_pedido);
CREATE INDEX IF NOT EXISTS idx_pedidos_updated_at ON pedidos (updated_at);
CREATE INDEX IF NOT EXISTS idx_pedidos_cliente ON pedidos (id_cliente);
CREATE INDEX IF NOT EXISTS idx_pedidos_restaurante ON pedidos (id_restaurante);
CREATE INDEX IF NOT EXISTS idx_pedidos_status ON pedidos (status_pedido);
CREATE INDEX IF NOT EXISTS idx_itens_pedido_pedido ON itens_pedido (id_pedido);
CREATE INDEX IF NOT EXISTS idx_enderecos_cliente ON enderecos_cliente (id_cliente);
CREATE INDEX IF NOT EXISTS idx_enderecos_cliente_ativo ON enderecos_cliente (id_cliente, status_ativo);
CREATE INDEX IF NOT EXISTS idx_clientes_updated_at ON clientes (updated_at);
CREATE INDEX IF NOT EXISTS idx_cardapio_restaurante ON cardapio (id_restaurante);
