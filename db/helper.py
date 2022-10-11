import sqlite3 as sq
from typing import Optional

from db.tables import USERS, ASSETS
from asset import AssetData, api
from exceptions import PortfolioError


def pragma(func):
    """Function sends the PRAGMA statement to the database after opening the connection"""
    def wrapper(self, *args, **kwargs):
        self.cur.execute('PRAGMA foreign_keys = ON')
        result = func(self, *args, **kwargs)
        self.conn.commit()
        return result
    return wrapper


class DBot:
    __db_path = 'db/crypto_data.db'

    def __init__(self):
        self.conn = sq.connect(self.__db_path)
        self.cur = self.conn.cursor()

    @pragma
    def create_tables(self):
        self.cur.execute(USERS)
        self.cur.execute(ASSETS)

    @pragma
    def register_new_user(self, user: tuple) -> str:
        message = '🔴 You are already registered'
        if (user[0], ) not in self.cur.execute('SELECT user_id FROM USERS').fetchall():
            self.cur.execute('INSERT INTO USERS(user_id, user_name, username) VALUES(?, ?, ?)', user)
            message = f'🟢 Hello, <b>{user[1]}</b>! I\'m Telegram bot that can help you to track your crypto assets.'
        return message

    def __get_assets(self, user_id: int) -> Optional[list[str]]:
        req = self.cur.execute('SELECT coin_symbol FROM ASSETS WHERE user_id = ?', (user_id,)).fetchall()
        return [sym[0] for sym in req] if req else []

    @pragma
    def add_asset(self, asset: AssetData):
        asset.symbol = asset.symbol.upper()
        req = 'INSERT INTO ASSETS(coin_symbol, amount, user_id) VALUES(?, ?, ?)', \
              (
                  asset.symbol,
                  asset.amount,
                  asset.user_id
              )
        message = f'🟢 You have successfully added {asset.amount} {asset.symbol} to your portfolio'

        if asset.symbol in self.__get_assets(user_id=asset.user_id):

            req = 'UPDATE ASSETS SET amount = ? WHERE coin_symbol = ? AND user_id = ?', \
                  (
                      asset.amount,
                      asset.symbol,
                      asset.user_id
                  )
            message = f'🟢 You have successfully changed {asset.symbol} amount'
        self.cur.execute(*req)

        return message

    @pragma
    def del_asset(self, asset: str, user_id: int) -> str:
        asset = asset.upper()
        message = f'🔴 {asset} not found in your portfolio'
        if asset and asset in self.__get_assets(user_id):
            self.cur.execute('DELETE FROM ASSETS WHERE coin_symbol = ? and user_id = ?', (asset, user_id))
            message = f'🟢 You have successfully deleted {asset} from your portfolio'
        return message

    @pragma
    def reset_assets(self, user_id: int) -> str:
        message = '🔴 Empty portfolio'
        if self.__get_assets(user_id):
            self.cur.execute('DELETE FROM ASSETS WHERE user_id = ?', (user_id,))
            message = '🟢 Your portfolio has been restored'
        return message

    @pragma
    def update_assets(self, user_id: int):
        if not self.__get_assets(user_id):
            raise PortfolioError(f'🔴 Portfolio {user_id} is empty')

        assets = self.cur.execute(f'''SELECT coin_symbol, amount, value
                                    FROM ASSETS WHERE user_id = {user_id}''').fetchall()
        assets = {
            data[0]: [None, data[0], None, data[1], data[2], None, None, user_id] for data in assets
        }
        old_total = sum(val[4] for val in assets.values())

        request = api.connect(','.join([coin for coin in assets.keys()]))['data']

        for coin, data in request.items():
            prev_value = assets[coin][4]
            assets[coin][0] = data[0]['name']
            assets[coin][2] = data[0]['quote']['USD']['price']
            assets[coin][4] = assets[coin][2] * float(assets[coin][3])
            assets[coin][5] = assets[coin][4] - prev_value
            assets[coin][6] = assets[coin][4] / prev_value * 100 - 100 if prev_value > 0 else 100.0

        total = sum(val[4] for val in assets.values())
        total_change = round(total - old_total, 4)
        total_change_percent = total / old_total * 100 - 100 if old_total > 0 else 100.0

        self.reset_assets(user_id)
        self.cur.executemany('INSERT INTO ASSETS VALUES(?, ?, ?, ?, ?, ?, ?, ?)', assets.values())

        return assets.values(), total, total_change, total_change_percent
