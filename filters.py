from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

class IsAdminFilter(BoundFilter):
    """
    Filter that checks for admin rights existence
    """
    key = "is_admin"

    def __init__(self, is_admin: bool):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.is_chat_admin() == self.is_admin