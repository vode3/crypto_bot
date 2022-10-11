from typing import Optional
from requests import Session, HTTPError
from random import choice


class APIHelper:

    URL = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    KEYS = (
        '973148fa-c510-452f-82a0-b5416f2e2789',
        '5938260c-c359-474b-9e32-c87b72adc64d',
        '191a26b8-2661-4dd0-8d68-b8bd1442f584',
        '6682937e-2a83-4ad9-bb82-ff0111bf07b2',
        '8a716d22-d3c7-4003-a5ab-f4fd66fc55fa',
        'df5d3b6c-fb96-4a1a-853c-7619fc4545c6',
        'fe45ab7f-a17b-44d6-9e94-8469a1a47a0f',
        'a0ca11de-f466-4be0-bbbd-0f783815f776',
        '1cc0da45-0456-4a9b-8920-2ce550b62fa1',
    )

    def connect(self, symbol: str, check: bool = False) -> Optional[dict]:
        parameters = {
            'symbol': symbol,
            'convert': 'USD',
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': choice(self.KEYS),
        }

        with Session() as sess:
            req = sess.get(
                self.URL,
                params=parameters,
                headers=headers,
            )
            try:
                req.raise_for_status()
                if not check or req.json()['data'][symbol]:
                    return req.json()
            except HTTPError:
                pass
