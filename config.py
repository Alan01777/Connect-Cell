"""
Configurações centralizadas do projeto Connect-Cell
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List


class Status(Enum):
    """Status dos serviços"""
    EM_ANDAMENTO = "EM ANDAMENTO"
    ENTREGUE = "ENTREGUE"
    DEVOLUCAO = "DEVOLUÇÃO"
    FINALIZADO = "FINALIZADO"
    ORCAMENTO = "ORÇAMENTO"
    OUTROS = "OUTROS"


class Categoria(Enum):
    """Categorias de serviços"""
    REPAROS_HARDWARE = "REPAROS HARDWARE"
    REPAROS_SOFTWARE = "REPAROS SOFTWARE"
    VENDAS_DISPOSITIVOS = "VENDAS DISPOSITIVOS"
    VENDAS_HARDWARE = "VENDAS HARDWARE"
    VENDAS_ACESSORIOS = "VENDAS ACESSÓRIOS"
    OUTROS = "OUTROS"


class FormaPagamento(Enum):
    """Formas de pagamento"""
    DINHEIRO = "DINHEIRO"
    CREDITO = "CREDITO"
    DEBITO = "DEBITO"
    PIX = "PIX"
    OUTROS = "OUTROS"


class Tecnico(Enum):
    """Técnicos disponíveis"""
    TIAGO = "TIAGO"
    VALDERI = "VALDERI"


@dataclass
class ColorPalette:
    """Paleta de cores do dashboard"""
    blue: str = "#1f77b4"
    red: str = "#d62728"
    green: str = "#2ca02c"
    purple: str = "#9467bd"
    orange: str = "#ff7f0e"
    yellow: str = "#ffbb78"
    gray: str = "#7f7f7f"
    pink: str = "#e377c2"

    # Cores por categoria
    category_colors: Dict[str, str] = None

    # Cores por técnico
    technician_colors: Dict[str, str] = None

    def __post_init__(self):
        self.category_colors = {
            Categoria.REPAROS_HARDWARE.value: self.blue,
            Categoria.REPAROS_SOFTWARE.value: self.purple,
            Categoria.VENDAS_DISPOSITIVOS.value: self.green,
            Categoria.VENDAS_HARDWARE.value: self.yellow,
            Categoria.VENDAS_ACESSORIOS.value: self.orange,
            Categoria.OUTROS.value: self.red,
        }

        self.technician_colors = {
            Tecnico.TIAGO.value: self.blue,
            Tecnico.VALDERI.value: self.red,
        }


@dataclass
class ChartConfig:
    """Configurações dos gráficos"""
    default_width: int = 1050
    default_height: int = 500  # Aumentado para melhor visualização em 1080p
    mobile_width: int = 800
    mobile_height: int = 400

    # Usar largura responsiva
    use_container_width: bool = True

    # Configurações de layout
    font_size: int = 14
    title_font_size: int = 18

    # Altura mínima para gráficos principais
    min_chart_height: int = 450


@dataclass
class AppConfig:
    """Configurações gerais da aplicação"""
    app_name: str = "Connect-Cell Dashboard"
    page_icon: str = "📱"
    layout: str = "wide"

    # Cache
    cache_ttl: int = 3600  # 1 hora em segundos

    # Formato de datas
    date_format: str = "%d/%m/%Y"
    date_format_display: str = "DD/MM/YYYY"

    # Colunas do DataFrame
    columns: Dict[str, str] = None

    # Percentuais de técnico
    technician_percentages: List[float] = None

    def __post_init__(self):
        self.columns = {
            "DATA": "DATA",
            "CLIENTE": "CLIENTE",
            "CONTATO": "CONTATO",
            "STATUS": "STATUS",
            "PRODUTO_SERVICO": "PRODUTO/SERVIÇO",
            "CATEGORIA": "CATEGORIA",
            "DESPESAS": "DESPESAS",
            "FATURAMENTO": "FATURAMENTO",
            "TECNICO": "TECNICO",
            "PERCENT_TECNICO": "% DO TÉCNICO",
            "LUCRO_BRUTO": "LUCRO BRUTO",
            "VALOR_TECNICO": "VALOR DO TÉCNICO",
            "LUCRO_LIQUIDO": "LUCRO LIQUIDO",
            "FORMA_PAGAMENTO": "F/PAGAMENTO",
        }

        self.technician_percentages = [0.3, 0.5, 0.8, 1.0]


# Instâncias globais
COLORS = ColorPalette()
CHART_CONFIG = ChartConfig()
APP_CONFIG = AppConfig()


# Mapeamento de nomes de categorias (para exibição)
CATEGORY_DISPLAY_NAMES = {
    Categoria.REPAROS_HARDWARE.value: "R. Hardware",
    Categoria.REPAROS_SOFTWARE.value: "R. de Software",
    Categoria.VENDAS_DISPOSITIVOS.value: "V. de Dispositivos",
    Categoria.VENDAS_HARDWARE.value: "V. de Hardware",
    Categoria.VENDAS_ACESSORIOS.value: "V. de Acessórios",
    Categoria.OUTROS.value: "Outros",
}


def get_status_options() -> List[str]:
    """Retorna lista de status disponíveis"""
    return [s.value for s in Status]


def get_categoria_options() -> List[str]:
    """Retorna lista de categorias disponíveis"""
    return [c.value for c in Categoria]


def get_forma_pagamento_options() -> List[str]:
    """Retorna lista de formas de pagamento disponíveis"""
    return [f.value for f in FormaPagamento]


def get_tecnico_options() -> List[str]:
    """Retorna lista de técnicos disponíveis"""
    return [t.value for t in Tecnico]
