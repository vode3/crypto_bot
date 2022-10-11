class SymbolError(Exception):
    """The coin's symbol is non-string type or CoinMarketCap API returned None"""


class AmountError(Exception):
    """The amount is not integer or float"""


class PortfolioError(Exception):
    """Portfolio is not found or empty"""
