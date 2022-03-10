from typing import TypedDict

from telegram import Message
from telegram import Update
from telegram.ext import CallbackContext as _CallbackContext

from .models.item import Item
from .models.legal_entity import LegalEntity


class InvoiceData(TypedDict):
    legal_entity: LegalEntity
    items: list[Item]


class UserData(TypedDict):
    invoice: InvoiceData


class CallbackContext(_CallbackContext[UserData, dict, dict]):
    user_data: UserData


class MessageUpdate(Update):
    message: Message


__all__ = [
    'CallbackContext',
    'MessageUpdate',
]
