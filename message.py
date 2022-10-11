from typing import Optional


def get_emoji(x):
    return '⚪' if not x else '🟢' if x > 0 else '🔴'


def get_plus(x):
    return f'+{x}' if x > 0 else x


class Message:

    @classmethod
    def compile_message(cls, assets_data: tuple) -> str:
        assets, total, total_change, total_change_percent = assets_data

        portfolio = [
            cls.__format_message(data) for data in sorted(
                assets,
                key=lambda x: (x[6], x[4]),
                reverse=True)
        ]

        header = f'{"📈" if float(total_change) > 0 else "📉"} <b>Your updated assets are here!</b>\n\n' \
            if total_change else '<b>The value of your assets has not changed!</b>\n\n'
        footer = [f'\n{get_emoji(total_change)} <b>Total:</b> {round(total, 4)}$',
                  f' <b>({get_plus(total_change)}$ / ' 
                  f'{round(total_change_percent, 4)}%)</b>' if total_change else '']

        portfolio.insert(0, header)
        portfolio.extend(footer)

        return ''.join(portfolio)

    @classmethod
    def __format_message(cls, data_asset: tuple) -> str:
        data_asset = (round(v, 4) if isinstance(v, float) else v for v in data_asset)
        name, symbol, price, amount, value, change_value, change_percent, user_id = data_asset
        message: list[Optional[str]] = [None] * 2

        message[0] = f'{get_emoji(change_value)} <b>{symbol}</b> {value}$'
        message[1] = f' <b>({get_plus(change_value)}$ / ' \
                     f'{get_plus(change_percent)}%)</b>\n' if change_value else '\n'

        return ''.join(message)
