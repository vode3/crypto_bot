from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from db.helper import DBot
from exceptions import PortfolioError
from message import Message

db = DBot()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    match query.data:
        case 'refresh':
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton('REFRESH', callback_data='refresh')]]
            )
            try:
                reply_message = Message.compile_message(
                    assets_data=db.update_assets(
                        user_id=query.from_user.id
                    )
                )
            except PortfolioError as err:
                reply_message = err
            finally:
                await query.message.edit_text(
                    text=reply_message,
                    reply_markup=reply_markup
                )
