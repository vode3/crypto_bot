from attrs import define, field
from string import ascii_uppercase

from cmc_api_service import APIHelper
from exceptions import SymbolError, AmountError


ALLOWED_PUNCTUATION = f'$@-{ascii_uppercase}'
api = APIHelper()


@define
class AssetData:
    symbol: str = field(default='')
    amount: str | float = field(default=None)
    user_id: int = None

    @symbol.validator
    def check(self, attribute, value):
        value = value.upper()
        if not self.symbol or any(char not in ALLOWED_PUNCTUATION for char in value) \
                or not api.connect(value, True):
            raise SymbolError(f'🔴 Invalid symbol: CoinMarketCap API returned None. {value} is not supported')

    @amount.validator
    def check(self, attribute, value):
        try:
            if not self.amount or not 0 < float(value) < 1_000_000_000_000:
                raise AmountError(f'🔴 Invalid amount: {value} should be more than 0 and less than 1T')
        except ValueError:
            raise AmountError(f'🔴 Invalid amount: {value} should be a number')
