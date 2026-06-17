#!/usr/bin/env python3
"""Gera massa de dados fictícia para o banco origem SparkEats (Issue #7)."""

from __future__ import annotations

import os
import random
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

ROOT = Path(__file__).resolve().parents[1]
DDL_PATH = ROOT / "sql/ddl_origem_postgresql.sql"

DEFAULT_DATABASE_URL = (
    "postgresql://sparkeats:sparkeats_dev@localhost:5433/sparkeats"
)

# Volumes aprovados (PR #7)
N_CATEGORIAS = 10
N_ZONAS = 20
N_CUPONS = 50
N_RESTAURANTES = 500
ITENS_POR_RESTAURANTE = 20
N_CLIENTES = 10_000
N_ENTREGADORES = 500
N_PEDIDOS = 50_000
MIN_LINHAS_PRINCIPAL = 10_000

PEDIDO_BATCH = 2_500
INSERT_BATCH = 5_000

CATEGORIAS = [
    ("Pizza", "Pizzarias e massas"),
    ("Japonesa", "Sushi, temaki e culinária oriental"),
    ("Lanches", "Hamburguerias e sanduíches"),
    ("Brasileira", "Comida caseira"),
    ("Saudável", "Saladas e bowls"),
    ("Doces", "Sobremesas e açaí"),
    ("Árabe", "Esfiha e quibe"),
    ("Italiana", "Massas e risotos"),
    ("Chinesa", "Yakisoba e dim sum"),
    ("Vegetariana", "Opções sem carne"),
]

ZONAS_SC = [
    ("Centro", "Criciúma", "SC", "Sul", 4.99),
    ("Michel", "Criciúma", "SC", "Sul", 5.99),
    ("São Luiz", "Criciúma", "SC", "Sul", 6.49),
    ("Próspera", "Criciúma", "SC", "Sul", 5.49),
    ("Pinheirinho", "Criciúma", "SC", "Sul", 7.99),
    ("Milanese", "Criciúma", "SC", "Sul", 6.99),
    ("Cidade Nova", "Criciúma", "SC", "Sul", 5.99),
    ("Argentina", "Criciúma", "SC", "Sul", 6.49),
    ("Nossa Senhora da Salete", "Criciúma", "SC", "Sul", 7.49),
    ("Santa Bárbara", "Criciúma", "SC", "Sul", 8.49),
    ("São Cristóvão", "Criciúma", "SC", "Sul", 6.29),
    ("Imperatriz", "Criciúma", "SC", "Sul", 5.79),
    ("Vila São José", "Criciúma", "SC", "Sul", 6.89),
    ("Universitário", "Criciúma", "SC", "Sul", 5.59),
    ("Boa Vista", "Criciúma", "SC", "Sul", 6.19),
]

ZONAS_TO = [
    ("Plano Diretor Norte", "Palmas", "TO", "Norte", 7.50),
    ("Centro", "Araguaína", "TO", "Norte", 6.90),
    ("Setor Central", "Gurupi", "TO", "Norte", 6.50),
    ("Centro", "Paraíso do Tocantins", "TO", "Norte", 7.00),
    ("Bela Vista", "Porto Nacional", "TO", "Norte", 6.80),
]

MENU_TEMPLATES: dict[str, list[tuple[str, str, float]]] = {
    "Japonesa": [
        ("Combo Sushi 12 peças", "Salmão, atum e kani", 49.90),
        ("Combo Sushi 20 peças", "Seleção do chef", 69.90),
        ("Temaki Salmão", "Arroz, salmão fresco e cream cheese", 24.90),
        ("Temaki Atum", "Atum temperado com gergelim", 26.90),
        ("Hot Roll Philadelphia", "8 peças empanadas", 32.90),
        ("Hot Roll Skin", "Pele de salmão crocante", 29.90),
        ("Uramaki Califórnia", "8 peças com kani e abacate", 27.90),
        ("Sashimi Salmão 10 fatias", "Salmão fresco", 38.90),
        ("Yakisoba Frango", "Macarrão oriental com legumes", 34.90),
        ("Yakisoba Vegetariano", "Legumes e shimeji", 31.90),
        ("Sunomono", "Salada de pepino agridoce", 18.90),
        ("Edamame", "Vagem de soja com flor de sal", 16.90),
        ("Combo Temaki Duo", "2 temakis à escolha", 44.90),
        ("Combo Hot Especial", "Hot roll + uramaki", 52.90),
        ("Gunkan Salmão", "4 unidades", 22.90),
        ("Gunkan Atum", "4 unidades", 23.90),
        ("Missoshiru", "Sopa tradicional de missô", 12.90),
        ("Guioza Legumes", "6 unidades grelhadas", 21.90),
        ("Guioza Frango", "6 unidades grelhadas", 22.90),
        ("Combo Família Sushi", "40 peças variadas", 119.90),
    ],
    "Pizza": [
        ("Pizza Margherita G", "Molho, mussarela e manjericão", 54.90),
        ("Pizza Calabresa G", "Calabresa fatiada e cebola", 56.90),
        ("Pizza Frango Catupiry G", "Frango desfiado com catupiry", 58.90),
        ("Pizza Quatro Queijos G", "Mussarela, gorgonzola, parmesão e catupiry", 62.90),
        ("Pizza Portuguesa G", "Presunto, ovos, cebola e azeitona", 59.90),
        ("Pizza Vegetariana G", "Legumes selecionados", 57.90),
        ("Pizza Bacon G", "Bacon crocante e mussarela", 61.90),
        ("Combo 2 Pizzas M", "Duas pizzas médias", 89.90),
        ("Pizza Doce Brigadeiro M", "Chocolate e granulado", 42.90),
        ("Pizza Doce Romeu e Julieta M", "Goiabada e queijo", 41.90),
        ("Borda Recheada Catupiry", "Adicional para pizza G", 12.90),
        ("Pizza Atum G", "Atum sólido e cebola", 58.90),
        ("Pizza Pepperoni G", "Pepperoni e mussarela", 63.90),
        ("Pizza Napolitana G", "Tomate, alho e azeite", 55.90),
        ("Combo Pizza + Refri 2L", "Pizza M + refrigerante", 72.90),
        ("Pizza Mussarela M", "Clássica mussarela", 44.90),
        ("Pizza Brócolis G", "Brócolis e alho", 57.90),
        ("Pizza Strogonoff Frango G", "Strogonoff de frango", 60.90),
        ("Pizza Marguerita M", "Versão média", 46.90),
        ("Combo Família 3 Pizzas G", "Três sabores", 149.90),
    ],
    "Lanches": [
        ("X-Burger Clássico", "Hambúrguer 120g, queijo e salada", 28.90),
        ("X-Bacon", "Bacon crocante e cheddar", 32.90),
        ("X-Salada", "Hambúrguer com salada completa", 29.90),
        ("X-Tudo", "Hambúrguer completo", 36.90),
        ("X-Frango", "Filé de frango grelhado", 27.90),
        ("Combo X-Burger", "Sanduíche + batata + refri", 42.90),
        ("Combo X-Bacon", "Sanduíche + batata + refri", 45.90),
        ("Smash Burger Duplo", "Dois smash 80g", 38.90),
        ("Smash Burger Triplo", "Três smash 80g", 44.90),
        ("Cheddar Melt", "Hambúrguer com cheddar cremoso", 34.90),
        ("Batata Frita M", "Porção média", 18.90),
        ("Batata Frita G", "Porção grande", 24.90),
        ("Onion Rings", "Anéis de cebola empanados", 22.90),
        ("Milkshake Morango", "400ml", 19.90),
        ("Milkshake Chocolate", "400ml", 19.90),
        ("Wrap Frango", "Frango grelhado com salada", 26.90),
        ("Wrap Vegetariano", "Grão-de-bico e legumes", 25.90),
        ("Hot Dog Especial", "Salsicha, purê e batata palha", 21.90),
        ("Combo Kids", "Mini burger + suco", 24.90),
        ("Combo Duplo Smash", "Dois smash + batata G", 52.90),
    ],
    "Brasileira": [
        ("PF Executivo", "Arroz, feijão, bife e salada", 32.90),
        ("PF Frango Grelhado", "Arroz, feijão, frango e legumes", 29.90),
        ("PF Peixe Grelhado", "Arroz, feijão, peixe e salada", 34.90),
        ("Feijoada Completa", "Acompanhamentos tradicionais", 38.90),
        ("Strogonoff Frango", "Arroz e batata palha", 31.90),
        ("Strogonoff Carne", "Arroz e batata palha", 35.90),
        ("Escondidinho Frango", "Purê de mandioca", 33.90),
        ("Escondidinho Carne Seca", "Purê de mandioca", 36.90),
        ("Galinhada", "Prato regional", 30.90),
        ("Moqueca Peixe", "Arroz e pirão", 42.90),
        ("Salada Caesar Frango", "Folhas, croutons e frango", 27.90),
        ("Sopa de Legumes", "Porção individual", 18.90),
        ("Marmita Fit", "Arroz integral, frango e salada", 28.90),
        ("Marmita Executiva", "Arroz, feijão, proteína e salada", 26.90),
        ("Combo PF + Suco", "PF + suco natural", 36.90),
        ("Bife Acebolado", "Arroz, feijão e fritas", 33.90),
        ("Parmegiana Frango", "Arroz, fritas e salada", 37.90),
        ("Lasanha Bolonhesa", "Porção individual", 29.90),
        ("Risoto Frango", "Cremoso com frango", 32.90),
        ("Combo Família Brasileira", "2 PFs + sobremesa", 64.90),
    ],
    "Saudável": [
        ("Bowl Proteico", "Arroz integral, frango e legumes", 34.90),
        ("Bowl Vegano", "Grão-de-bico, quinoa e legumes", 32.90),
        ("Salada Caesar", "Alface, croutons e parmesão", 26.90),
        ("Salada Tropical", "Folhas, manga e castanhas", 28.90),
        ("Wrap Integral Frango", "Frango e homus", 27.90),
        ("Wrap Integral Atum", "Atum e cream cheese light", 28.90),
        ("Smoothie Verde", "Couve, maçã e gengibre", 18.90),
        ("Smoothie Frutas Vermelhas", "Mix de frutas", 19.90),
        ("Açaí 500ml", "Com granola e banana", 22.90),
        ("Açaí 700ml", "Com granola, banana e mel", 28.90),
        ("Omelete Fit", "Claras, espinafre e tomate", 24.90),
        ("Panqueca Proteica", "Aveia, banana e whey", 21.90),
        ("Sopa Detox", "Legumes leves", 19.90),
        ("Combo Bowl + Suco", "Bowl + suco verde", 42.90),
        ("Poke Salmão", "Arroz, salmão e vegetais", 39.90),
        ("Poke Frango", "Arroz, frango e vegetais", 34.90),
        ("Salada de Quinoa", "Quinoa, legumes e feta", 29.90),
        ("Iogurte com Granola", "Iogurte natural e frutas", 16.90),
        ("Combo Fit Duplo", "2 bowls médios", 58.90),
        ("Água de Coco 500ml", "Natural", 8.90),
    ],
    "Doces": [
        ("Açaí 400ml", "Com granola", 18.90),
        ("Açaí 700ml", "Com frutas", 24.90),
        ("Brownie Tradicional", "Unidade", 12.90),
        ("Brownie com Sorvete", "Brownie quente", 19.90),
        ("Pudim de Leite", "Fatia generosa", 14.90),
        ("Mousse de Maracujá", "Porção individual", 13.90),
        ("Torta de Limão", "Fatia", 15.90),
        ("Combo Açaí Duplo", "2 açaís 500ml", 38.90),
        ("Milkshake Ovomaltine", "400ml", 21.90),
        ("Waffle com Nutella", "Waffle belga", 22.90),
        ("Crepe Doce", "Banana e canela", 17.90),
        ("Sorvete 2 Bolas", "Sabores variados", 14.90),
        ("Picolé Artesanal", "Unidade", 9.90),
        ("Bolo de Cenoura", "Fatia com cobertura", 11.90),
        ("Brigadeiro Gourmet 4un", "Tradicional e gourmet", 16.90),
        ("Combo Sobremesa", "Brownie + milkshake", 32.90),
        ("Taça de Frutas", "Frutas frescas", 18.90),
        ("Smoothie Açaí", "400ml", 20.90),
        ("Cookie Chocolate", "Unidade grande", 10.90),
        ("Combo Família Doce", "4 sobremesas variadas", 54.90),
    ],
    "Árabe": [
        ("Esfiha Carne 12un", "Carne temperada", 32.90),
        ("Esfiha Queijo 12un", "Queijo e orégano", 30.90),
        ("Esfiha Calabresa 12un", "Calabresa e cebola", 31.90),
        ("Kibe Assado 6un", "Tradicional", 28.90),
        ("Kibe Frito 6un", "Crocante", 29.90),
        ("Shawarma Frango", "Pão sírio recheado", 26.90),
        ("Shawarma Carne", "Pão sírio recheado", 28.90),
        ("Homus com Pão", "Pasta de grão-de-bico", 22.90),
        ("Babaganoush", "Berinjela defumada", 23.90),
        ("Tabule", "Salada de trigo", 19.90),
        ("Combo Esfiha 24un", "Carne e queijo", 58.90),
        ("Prato Executivo Árabe", "Arroz, kibe e salada", 36.90),
        ("Kafta Grelhada", "Com arroz e salada", 38.90),
        ("Falafel 8un", "Grão-de-bico", 24.90),
        ("Esfihas Abertas Mix 18un", "Sabores variados", 45.90),
        ("Suco de Maracujá", "300ml", 9.90),
        ("Combo Shawarma + Suco", "Shawarma + bebida", 32.90),
        ("Quibe Cru 4un", "Tradicional", 22.90),
        ("Salada Árabe", "Folhas e grão-de-bico", 21.90),
        ("Combo Família Árabe", "Esfihas + kibes + homus", 79.90),
    ],
    "Italiana": [
        ("Spaghetti Bolonhesa", "Molho de carne", 38.90),
        ("Spaghetti Carbonara", "Bacon e parmesão", 40.90),
        ("Lasanha Bolonhesa", "Individual", 35.90),
        ("Lasanha Quatro Queijos", "Individual", 36.90),
        ("Risoto Funghi", "Cogumelos frescos", 42.90),
        ("Risoto Frango", "Cremoso", 39.90),
        ("Penne ao Pesto", "Manjericão e parmesão", 37.90),
        ("Nhoque ao Sugo", "Molho de tomate", 34.90),
        ("Nhoque Quatro Queijos", "Cremoso", 36.90),
        ("Ravioli Ricota Espinafre", "Molho branco", 41.90),
        ("Combo Massa + Salada", "Prato + salada", 48.90),
        ("Bruschetta", "4 unidades", 22.90),
        ("Caprese", "Mussarela de búfala e tomate", 28.90),
        ("Tiramisu", "Sobremesa italiana", 18.90),
        ("Panna Cotta", "Com calda de frutas", 16.90),
        ("Pizza Margherita Italiana", "Forno a lenha", 52.90),
        ("Fettuccine Alfredo", "Molho branco", 39.90),
        ("Combo Casal Italiano", "2 massas + tiramisu", 82.90),
        ("Sopa Minestrone", "Legumes e feijão branco", 24.90),
        ("Combo Família Massas", "Lasanha G + nhoque", 89.90),
    ],
    "Chinesa": [
        ("Yakisoba Frango", "Macarrão oriental", 34.90),
        ("Yakisoba Carne", "Macarrão oriental", 36.90),
        ("Yakisoba Vegetariano", "Legumes", 31.90),
        ("Yakisoba Camarão", "Camarão e legumes", 42.90),
        ("Frango Xadrez", "Arroz e legumes", 33.90),
        ("Frango Agridoce", "Arroz e legumes", 32.90),
        ("Carne com Brócolis", "Molho oriental", 35.90),
        ("Rolinho Primavera 4un", "Vegetais", 18.90),
        ("Rolinho Primavera 8un", "Vegetais", 28.90),
        ("Dim Sum Mix 6un", "Cestinha variada", 29.90),
        ("Arroz Chop Suey", "Legumes e ovos", 28.90),
        ("Combo Yakisoba M", "Yakisoba + rolinho", 42.90),
        ("Combo Yakisoba G", "Yakisoba G + bebida", 48.90),
        ("Sopa Agripicante", "Tradicional", 22.90),
        ("Macarrão Oriental Vegetariano", "Shimeji e legumes", 30.90),
        ("Lombo Agridoce", "Arroz e legumes", 37.90),
        ("Combo Família Chinês", "2 yakisobas G", 72.90),
        ("Frango Empanado Oriental", "Com molho agridoce", 31.90),
        ("Tofu Grelhado", "Legumes salteados", 29.90),
        ("Chá Gelado", "Limão ou pêssego", 8.90),
    ],
    "Vegetariana": [
        ("Burger Vegetal", "Hambúrguer de grão-de-bico", 29.90),
        ("Burger Cogumelos", "Shiitake grelhado", 31.90),
        ("Wrap Vegetariano", "Legumes e homus", 26.90),
        ("Salada Buddha Bowl", "Quinoa e legumes", 32.90),
        ("Lasanha Vegetariana", "Berinjela e abobrinha", 34.90),
        ("Risoto Vegetariano", "Cogumelos e aspargos", 38.90),
        ("Nhoque Integral", "Molho de tomate", 30.90),
        ("Strogonoff Cogumelos", "Arroz e batata palha", 33.90),
        ("Esfiha Vegetariana 12un", "Legumes e queijo", 29.90),
        ("Pizza Vegetariana G", "Legumes grelhados", 54.90),
        ("Combo Veggie", "Burger + salada", 44.90),
        ("Smoothie Verde", "Couve e frutas", 18.90),
        ("Açaí Vegano", "Sem mel, com granola", 22.90),
        ("Tofu Teriyaki", "Arroz e legumes", 31.90),
        ("Falafel Bowl", "Grão-de-bico e tahine", 30.90),
        ("Panqueca Integral", "Recheio de legumes", 27.90),
        ("Sopa de Legumes", "Cremosa", 19.90),
        ("Combo Família Veg", "2 burgers + 2 saladas", 68.90),
        ("Iogurte Vegetal", "Com granola", 15.90),
        ("Hummus Bowl", "Homus, quinoa e salada", 29.90),
    ],
}

EXCLUDED_KEYWORDS = (
    "porco",
    "suíno",
    "suino",
    "fígado",
    "figado",
    "coração",
    "coracao",
    "coração de galinha",
)

STATUS_PEDIDO = (
    ["ENTREGUE"] * 68
    + ["CANCELADO"] * 10
    + ["EM_TRANSITO"] * 12
    + ["PREPARANDO"] * 10
)
FORMAS_PAGAMENTO = ["PIX", "CARTAO", "DINHEIRO"]

TABELAS_PRINCIPAIS = (
    "clientes",
    "enderecos_cliente",
    "cardapio",
    "pedidos",
    "itens_pedido",
    "pagamentos",
    "avaliacoes",
)


def get_engine() -> Engine:
    url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    return create_engine(url, future=True)


def apply_ddl(engine: Engine) -> None:
    raw = DDL_PATH.read_text(encoding="utf-8")
    statements: list[str] = []
    buffer: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        buffer.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(buffer))
            buffer = []
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


def random_ts(fake: Faker) -> datetime:
    return fake.date_time_between(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2026, 6, 10, 23, 59, 59),
    )


def random_updated_at(fake: Faker, created: datetime) -> datetime:
    if random.random() > 0.15:
        return created
    return fake.date_time_between(start_date=created, end_date=datetime.now())


def seed_categorias(conn) -> None:
    now = datetime.now()
    conn.execute(
        text(
            """
            INSERT INTO categorias_restaurante (nome, descricao, created_at, updated_at)
            VALUES (:nome, :descricao, :created_at, :updated_at)
            """
        ),
        [
            {
                "nome": n,
                "descricao": d,
                "created_at": now,
                "updated_at": now,
            }
            for n, d in CATEGORIAS
        ],
    )


def seed_zonas(conn) -> None:
    now = datetime.now()
    rows = []
    for bairro, cidade, uf, regiao, taxa in ZONAS_SC + ZONAS_TO:
        rows.append(
            {
                "nome_bairro": bairro,
                "cidade": cidade,
                "estado": uf,
                "regiao": regiao,
                "taxa_entrega": taxa,
                "created_at": now,
                "updated_at": now,
            }
        )
    conn.execute(
        text(
            """
            INSERT INTO zonas_entrega
            (nome_bairro, cidade, estado, regiao, taxa_entrega, created_at, updated_at)
            VALUES
            (:nome_bairro, :cidade, :estado, :regiao, :taxa_entrega, :created_at, :updated_at)
            """
        ),
        rows,
    )


def seed_cupons(conn, fake: Faker) -> list[int]:
    now = datetime.now()
    cupons = []
    for i in range(N_CUPONS):
        created = random_updated_at(fake, now)
        cupons.append(
            {
                "codigo": f"SPARK{i + 100:03d}",
                "descricao": fake.sentence(nb_words=4)[:255],
                "percentual": random.choice([5, 10, 15, None]),
                "valor_fixo": random.choice([None, 5, 10, 15, 20]),
                "dt_inicio": fake.date_between(start_date="-3y", end_date="-1y"),
                "dt_fim": fake.date_between(start_date="-1y", end_date="+1y"),
                "ativo": random.random() > 0.15,
                "created_at": created,
                "updated_at": created,
            }
        )
    conn.execute(
        text(
            """
            INSERT INTO cupons
            (codigo, descricao, percentual, valor_fixo, dt_inicio, dt_fim, ativo,
             created_at, updated_at)
            VALUES
            (:codigo, :descricao, :percentual, :valor_fixo, :dt_inicio, :dt_fim, :ativo,
             :created_at, :updated_at)
            """
        ),
        cupons,
    )
    return [row[0] for row in conn.execute(text("SELECT id_cupom FROM cupons ORDER BY id_cupom"))]


def seed_restaurantes(conn, fake: Faker) -> tuple[list[int], dict[int, str]]:
    now = datetime.now()
    n_zonas = len(ZONAS_SC) + len(ZONAS_TO)
    rows = []
    cat_by_rest: dict[int, str] = {}
    for i in range(N_RESTAURANTES):
        cat_idx = (i % N_CATEGORIAS) + 1
        created = random_updated_at(fake, now)
        rows.append(
            {
                "id_categoria": cat_idx,
                "id_zona": random.randint(1, n_zonas),
                "nome_fantasia": f"{fake.company()[:40]} {random.choice(['Grill', 'Kitchen', 'Express', 'Food'])}",
                "razao_social": fake.company()[:180],
                "cnpj": fake.unique.cnpj(),
                "taxa_comissao": round(random.uniform(10, 25), 2),
                "status": random.choice(["ATIVO", "ATIVO", "ATIVO", "INATIVO"]),
                "created_at": created,
                "updated_at": created,
            }
        )
    conn.execute(
        text(
            """
            INSERT INTO restaurantes
            (id_categoria, id_zona, nome_fantasia, razao_social, cnpj, taxa_comissao, status,
             created_at, updated_at)
            VALUES
            (:id_categoria, :id_zona, :nome_fantasia, :razao_social, :cnpj, :taxa_comissao, :status,
             :created_at, :updated_at)
            """
        ),
        rows,
    )
    ids = [row[0] for row in conn.execute(text("SELECT id_restaurante FROM restaurantes ORDER BY id_restaurante"))]
    cat_rows = conn.execute(
        text("SELECT id_restaurante, id_categoria FROM restaurantes ORDER BY id_restaurante")
    ).fetchall()
    cat_by_rest = {rid: CATEGORIAS[cid - 1][0] for rid, cid in cat_rows}
    return ids, cat_by_rest


def _item_allowed(nome: str) -> bool:
    lower = nome.lower()
    return not any(word in lower for word in EXCLUDED_KEYWORDS)


def seed_cardapio(
    conn, restaurante_ids: list[int], cat_by_rest: dict[int, str], fake: Faker
) -> dict[int, list[dict]]:
    now = datetime.now()
    itens: list[dict] = []
    cardapio_por_restaurante: dict[int, list[dict]] = {}

    for rid in restaurante_ids:
        cat_name = cat_by_rest.get(rid, CATEGORIAS[0][0])
        templates = [t for t in MENU_TEMPLATES.get(cat_name, MENU_TEMPLATES["Brasileira"]) if _item_allowed(t[0])]
        if len(templates) < ITENS_POR_RESTAURANTE:
            templates = templates + MENU_TEMPLATES["Brasileira"]
        selected = templates[:ITENS_POR_RESTAURANTE]
        cardapio_por_restaurante[rid] = []
        for nome, desc, preco_base in selected:
            preco = round(preco_base * random.uniform(0.95, 1.08), 2)
            created = random_updated_at(fake, now)
            itens.append(
                {
                    "id_restaurante": rid,
                    "nome_item": nome[:120],
                    "descricao": desc[:255],
                    "preco": preco,
                    "disponivel": random.random() > 0.04,
                    "created_at": created,
                    "updated_at": created,
                }
            )

    for i in range(0, len(itens), INSERT_BATCH):
        conn.execute(
            text(
                """
                INSERT INTO cardapio
                (id_restaurante, nome_item, descricao, preco, disponivel, created_at, updated_at)
                VALUES
                (:id_restaurante, :nome_item, :descricao, :preco, :disponivel,
                 :created_at, :updated_at)
                """
            ),
            itens[i : i + INSERT_BATCH],
        )

    rows = conn.execute(
        text("SELECT id_item, id_restaurante, preco FROM cardapio ORDER BY id_item")
    )
    for r in rows:
        cardapio_por_restaurante.setdefault(r[1], []).append(
            {"id_item": r[0], "id_restaurante": r[1], "preco": float(r[2])}
        )
    return cardapio_por_restaurante


def seed_clientes(conn, fake: Faker) -> list[int]:
    rows = []
    for _ in range(N_CLIENTES):
        cadastro = fake.date_between(start_date=date(2022, 1, 1), end_date=date(2025, 12, 31))
        created = datetime.combine(cadastro, datetime.min.time()) + timedelta(
            hours=random.randint(8, 22)
        )
        rows.append(
            {
                "nome": fake.name()[:150],
                "email": fake.unique.email()[:180],
                "telefone": fake.phone_number()[:20],
                "cpf": fake.unique.cpf(),
                "data_inicio": cadastro,
                "data_fim": None,
                "status_ativo": True,
                "created_at": created,
                "updated_at": random_updated_at(fake, created),
            }
        )
    for i in range(0, len(rows), INSERT_BATCH):
        conn.execute(
            text(
                """
                INSERT INTO clientes
                (nome, email, telefone, cpf, data_inicio, data_fim, status_ativo,
                 created_at, updated_at)
                VALUES
                (:nome, :email, :telefone, :cpf, :data_inicio, :data_fim, :status_ativo,
                 :created_at, :updated_at)
                """
            ),
            rows[i : i + INSERT_BATCH],
        )
    return [row[0] for row in conn.execute(text("SELECT id_cliente FROM clientes ORDER BY id_cliente"))]


def seed_enderecos(conn, cliente_ids: list[int], fake: Faker) -> None:
    zonas = ZONAS_SC + ZONAS_TO
    rows = []
    for cid in cliente_ids:
        qtd = 2 if random.random() < 0.20 else 1
        for idx in range(qtd):
            bairro, cidade, uf, _, _ = random.choice(zonas)
            inicio = fake.date_between(start_date=date(2022, 6, 1), end_date=date(2025, 6, 1))
            ativo = idx == qtd - 1
            fim = None
            if not ativo:
                fim = inicio + timedelta(days=random.randint(180, 540))
            created = datetime.combine(inicio, datetime.min.time())
            rows.append(
                {
                    "id_cliente": cid,
                    "logradouro": fake.street_name()[:200],
                    "numero": str(random.randint(1, 2500)),
                    "bairro": bairro[:100],
                    "cidade": cidade,
                    "estado": uf,
                    "cep": fake.postcode()[:10],
                    "complemento": f"Apto {random.randint(1, 200)}" if random.random() > 0.55 else None,
                    "principal": ativo,
                    "data_inicio": inicio,
                    "data_fim": fim,
                    "status_ativo": ativo,
                    "created_at": created,
                    "updated_at": random_updated_at(fake, created),
                }
            )
    for i in range(0, len(rows), INSERT_BATCH):
        conn.execute(
            text(
                """
                INSERT INTO enderecos_cliente
                (id_cliente, logradouro, numero, bairro, cidade, estado, cep, complemento,
                 principal, data_inicio, data_fim, status_ativo, created_at, updated_at)
                VALUES
                (:id_cliente, :logradouro, :numero, :bairro, :cidade, :estado, :cep, :complemento,
                 :principal, :data_inicio, :data_fim, :status_ativo, :created_at, :updated_at)
                """
            ),
            rows[i : i + INSERT_BATCH],
        )


def seed_entregadores(conn, fake: Faker) -> list[int]:
    n_zonas = len(ZONAS_SC) + len(ZONAS_TO)
    now = datetime.now()
    rows = [
        {
            "id_zona": random.randint(1, n_zonas),
            "nome": fake.name()[:150],
            "cpf": fake.unique.cpf(),
            "telefone": fake.phone_number()[:20],
            "veiculo": random.choice(["MOTO", "MOTO", "BICICLETA", "CARRO"]),
            "status": random.choice(["ATIVO", "ATIVO", "INATIVO"]),
            "created_at": random_updated_at(fake, now),
            "updated_at": random_updated_at(fake, now),
        }
        for _ in range(N_ENTREGADORES)
    ]
    conn.execute(
        text(
            """
            INSERT INTO entregadores
            (id_zona, nome, cpf, telefone, veiculo, status, created_at, updated_at)
            VALUES
            (:id_zona, :nome, :cpf, :telefone, :veiculo, :status, :created_at, :updated_at)
            """
        ),
        rows,
    )
    return [row[0] for row in conn.execute(text("SELECT id_entregador FROM entregadores ORDER BY id_entregador"))]


def _pedido_timestamps(
    data_pedido: datetime, status: str
) -> tuple[datetime | None, datetime | None, int | None]:
    coleta = None
    entrega = None
    tempo = None
    if status == "PREPARANDO":
        return coleta, entrega, tempo
    if status == "CANCELADO":
        return coleta, entrega, tempo
    coleta = data_pedido + timedelta(minutes=random.randint(15, 40))
    if status == "EM_TRANSITO":
        return coleta, entrega, random.randint(20, 50)
    entrega = coleta + timedelta(minutes=random.randint(18, 75))
    tempo = int((entrega - data_pedido).total_seconds() // 60)
    return coleta, entrega, tempo


def seed_pedidos_e_relacionados(
    conn,
    fake: Faker,
    cliente_ids: list[int],
    restaurante_ids: list[int],
    entregador_ids: list[int],
    cupom_ids: list[int],
    cardapio_por_restaurante: dict[int, list[dict]],
) -> None:
    fallback_menu = [m for items in cardapio_por_restaurante.values() for m in items[:3]]

    for batch_start in range(0, N_PEDIDOS, PEDIDO_BATCH):
        pedidos_batch: list[dict] = []
        for _ in range(min(PEDIDO_BATCH, N_PEDIDOS - batch_start)):
            data_pedido = random_ts(fake)
            status = random.choice(STATUS_PEDIDO)
            created = data_pedido
            pedidos_batch.append(
                {
                    "id_cliente": random.choice(cliente_ids),
                    "id_restaurante": random.choice(restaurante_ids),
                    "id_entregador": random.choice(entregador_ids),
                    "id_cupom": random.choice(cupom_ids + [None] * 8),
                    "data_hora_pedido": data_pedido,
                    "status_pedido": status,
                    "created_at": created,
                    "updated_at": random_updated_at(fake, created),
                }
            )

        conn.execute(
            text(
                """
                INSERT INTO pedidos
                (id_cliente, id_restaurante, id_entregador, id_cupom, data_hora_pedido,
                 status_pedido, valor_itens, taxa_entrega, desconto, valor_total,
                 created_at, updated_at)
                VALUES
                (:id_cliente, :id_restaurante, :id_entregador, :id_cupom, :data_hora_pedido,
                 :status_pedido, 0, 0, 0, 0, :created_at, :updated_at)
                """
            ),
            pedidos_batch,
        )

        inserted = conn.execute(
            text(
                """
                SELECT id_pedido, id_restaurante, data_hora_pedido, status_pedido, created_at
                FROM pedidos
                ORDER BY id_pedido DESC
                LIMIT :lim
                """
            ),
            {"lim": len(pedidos_batch)},
        ).fetchall()
        inserted = list(reversed(inserted))

        itens_rows: list[dict] = []
        pagamentos_rows: list[dict] = []
        avaliacoes_rows: list[dict] = []
        pedido_updates: list[dict] = []

        for id_pedido, id_restaurante, data_pedido, status, created in inserted:
            menu = cardapio_por_restaurante.get(id_restaurante) or fallback_menu
            coleta, entrega, tempo = _pedido_timestamps(data_pedido, status)

            qtd_itens_pedido = random.randint(1, 5)
            valor_itens = Decimal("0")
            for _ in range(qtd_itens_pedido):
                item = random.choice(menu)
                qtd = random.randint(1, 3)
                preco = Decimal(str(item["preco"]))
                subtotal = preco * qtd
                valor_itens += subtotal
                item_created = random_updated_at(fake, created)
                itens_rows.append(
                    {
                        "id_pedido": id_pedido,
                        "id_item": item["id_item"],
                        "quantidade": qtd,
                        "preco_unitario": preco,
                        "subtotal": subtotal,
                        "created_at": item_created,
                        "updated_at": item_created,
                    }
                )

            taxa_entrega = Decimal(str(round(random.uniform(4.99, 9.99), 2)))
            desconto = Decimal("0")
            if random.random() < 0.11:
                desconto = Decimal(str(round(float(valor_itens) * random.uniform(0.05, 0.15), 2)))
            valor_total = max(Decimal("0"), valor_itens + taxa_entrega - desconto)

            pedido_updates.append(
                {
                    "id_pedido": id_pedido,
                    "data_hora_coleta": coleta,
                    "data_hora_entrega": entrega,
                    "valor_itens": valor_itens,
                    "taxa_entrega": taxa_entrega,
                    "desconto": desconto,
                    "valor_total": valor_total,
                    "tempo_entrega_min": tempo,
                }
            )

            pag_created = random_updated_at(fake, created)
            pagamentos_rows.append(
                {
                    "id_pedido": id_pedido,
                    "forma_pagamento": random.choice(FORMAS_PAGAMENTO),
                    "status_pagamento": "ESTORNADO" if status == "CANCELADO" else "APROVADO",
                    "valor_pago": valor_total,
                    "dt_pagamento": data_pedido,
                    "created_at": pag_created,
                    "updated_at": pag_created,
                }
            )

            if status == "ENTREGUE" and random.random() > 0.15:
                nota = round(random.uniform(3.0, 5.0), 1)
                av_created = entrega or data_pedido
                avaliacoes_rows.append(
                    {
                        "id_pedido": id_pedido,
                        "nota_restaurante": nota,
                        "nota_entrega": round(max(1.0, min(5.0, nota + random.uniform(-0.5, 0.5))), 1),
                        "nota_geral": nota,
                        "comentario": fake.sentence(nb_words=8)[:500],
                        "dt_avaliacao": entrega or data_pedido,
                        "created_at": av_created,
                        "updated_at": av_created,
                    }
                )

        conn.execute(
            text(
                """
                UPDATE pedidos SET
                    data_hora_coleta = :data_hora_coleta,
                    data_hora_entrega = :data_hora_entrega,
                    valor_itens = :valor_itens,
                    taxa_entrega = :taxa_entrega,
                    desconto = :desconto,
                    valor_total = :valor_total,
                    tempo_entrega_min = :tempo_entrega_min
                WHERE id_pedido = :id_pedido
                """
            ),
            pedido_updates,
        )

        for i in range(0, len(itens_rows), INSERT_BATCH):
            conn.execute(
                text(
                    """
                    INSERT INTO itens_pedido
                    (id_pedido, id_item, quantidade, preco_unitario, subtotal, created_at, updated_at)
                    VALUES
                    (:id_pedido, :id_item, :quantidade, :preco_unitario, :subtotal,
                     :created_at, :updated_at)
                    """
                ),
                itens_rows[i : i + INSERT_BATCH],
            )

        for i in range(0, len(pagamentos_rows), INSERT_BATCH):
            conn.execute(
                text(
                    """
                    INSERT INTO pagamentos
                    (id_pedido, forma_pagamento, status_pagamento, valor_pago, dt_pagamento,
                     created_at, updated_at)
                    VALUES
                    (:id_pedido, :forma_pagamento, :status_pagamento, :valor_pago, :dt_pagamento,
                     :created_at, :updated_at)
                    """
                ),
                pagamentos_rows[i : i + INSERT_BATCH],
            )

        for i in range(0, len(avaliacoes_rows), INSERT_BATCH):
            conn.execute(
                text(
                    """
                    INSERT INTO avaliacoes
                    (id_pedido, nota_restaurante, nota_entrega, nota_geral, comentario,
                     dt_avaliacao, created_at, updated_at)
                    VALUES
                    (:id_pedido, :nota_restaurante, :nota_entrega, :nota_geral, :comentario,
                     :dt_avaliacao, :created_at, :updated_at)
                    """
                ),
                avaliacoes_rows[i : i + INSERT_BATCH],
            )

        print(f"  pedidos processados: {batch_start + len(pedidos_batch):,}/{N_PEDIDOS:,}")


def simulate_cliente_updates(conn, fake: Faker, cliente_ids: list[int]) -> None:
    """~8% dos clientes com updated_at recente (demo carga incremental / SCD)."""
    sample = random.sample(cliente_ids, k=int(len(cliente_ids) * 0.08))
    for cid in sample:
        conn.execute(
            text(
                """
                UPDATE clientes
                SET telefone = :telefone,
                    updated_at = :updated_at
                WHERE id_cliente = :id_cliente
                """
            ),
            {
                "id_cliente": cid,
                "telefone": fake.phone_number()[:20],
                "updated_at": fake.date_time_between(start_date="-30d", end_date="now"),
            },
        )


def print_counts(engine: Engine) -> None:
    tables = [
        "categorias_restaurante",
        "zonas_entrega",
        "cupons",
        "restaurantes",
        "cardapio",
        "clientes",
        "enderecos_cliente",
        "entregadores",
        "pedidos",
        "itens_pedido",
        "pagamentos",
        "avaliacoes",
    ]
    print("\n=== Contagem de registros ===")
    with engine.connect() as conn:
        for table in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
            print(f"  {table:25} {count:>8,}")
        print("\n=== Pedidos por ano ===")
        rows = conn.execute(
            text(
                """
                SELECT EXTRACT(YEAR FROM data_hora_pedido)::INT AS ano, COUNT(*) AS total
                FROM pedidos GROUP BY 1 ORDER BY 1
                """
            )
        ).fetchall()
        for ano, total in rows:
            print(f"  {ano}: {total:,}")


def validate_minimums(engine: Engine) -> None:
    errors: list[str] = []
    with engine.connect() as conn:
        for table in TABELAS_PRINCIPAIS:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
            if count < MIN_LINHAS_PRINCIPAL:
                errors.append(f"{table}: {count:,} < {MIN_LINHAS_PRINCIPAL:,}")
        pedidos = conn.execute(text("SELECT COUNT(*) FROM pedidos")).scalar_one()
        if pedidos < N_PEDIDOS:
            errors.append(f"pedidos: {pedidos:,} < {N_PEDIDOS:,}")
    if errors:
        print("\n=== FALHA na validação de volumes ===")
        for err in errors:
            print(f"  - {err}")
        raise SystemExit(1)
    print(f"\n=== Validação OK (≥ {MIN_LINHAS_PRINCIPAL:,} nas tabelas principais) ===")


def main() -> int:
    fake = Faker("pt_BR")
    Faker.seed(42)
    random.seed(42)

    print("SparkEats — seed banco origem")
    print(f"DDL: {DDL_PATH}")

    engine = get_engine()
    print("Aplicando DDL...")
    apply_ddl(engine)

    print("Gerando dados (pode levar alguns minutos)...")
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE TABLE avaliacoes, pagamentos, itens_pedido, pedidos,
                enderecos_cliente, entregadores, clientes, cardapio, restaurantes,
                cupons, zonas_entrega, categorias_restaurante RESTART IDENTITY CASCADE
                """
            )
        )
        seed_categorias(conn)
        seed_zonas(conn)
        cupom_ids = seed_cupons(conn, fake)
        restaurante_ids, cat_by_rest = seed_restaurantes(conn, fake)
        cardapio_por_restaurante = seed_cardapio(conn, restaurante_ids, cat_by_rest, fake)
        cliente_ids = seed_clientes(conn, fake)
        seed_enderecos(conn, cliente_ids, fake)
        entregador_ids = seed_entregadores(conn, fake)
        seed_pedidos_e_relacionados(
            conn,
            fake,
            cliente_ids,
            restaurante_ids,
            entregador_ids,
            cupom_ids,
            cardapio_por_restaurante,
        )
        simulate_cliente_updates(conn, fake, cliente_ids)

    print_counts(engine)
    validate_minimums(engine)
    print("\nSeed concluído com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
