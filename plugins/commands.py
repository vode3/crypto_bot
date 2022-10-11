from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db.helper import DBot
from exceptions import SymbolError, AmountError, PortfolioError
from asset import AssetData
from message import Message


db = DBot()


@Client.on_message(filters.command('start') & filters.private)
async def start(bot, message):
    user_data = (
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username
    )
    await message.reply_text(
        text=db.register_new_user(user_data)
    )


@Client.on_message(filters.command(['a', 'add', 'e', 'edit']) & filters.private)
async def add(bot, message):
    try:
        reply_message = db.add_asset(
            AssetData(*message.text.split()[1:],
                      user_id=message.from_user.id)
        )
    except (SymbolError, AmountError, ValueError) as err:
        reply_message = err
    finally:
        await message.reply_text(
            text=reply_message
        )


@Client.on_message(filters.private & filters.command(['c', 'check']))
async def check(bot, message):
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('REFRESH', callback_data='refresh')]]
    )
    try:
        reply_message = Message.compile_message(
            assets_data=db.update_assets(
                user_id=message.from_user.id
            )
        )
    except PortfolioError as err:
        reply_message = err
    finally:
        await message.reply_text(
            text=reply_message,
            reply_markup=reply_markup
        )


@Client.on_message(filters.private & filters.command(['d', 'del', 'delete']))
async def delete(bot, message):
    try:
        asset = message.text.split()[1]
    except IndexError:
        asset = ''
    finally:
        reply_message = db.del_asset(
            asset=asset,
            user_id=message.from_user.id
        )
        await message.reply_text(
            text=reply_message
        )
