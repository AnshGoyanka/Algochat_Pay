"""
Bot package - WhatsApp & Telegram integration
"""
from bot.command_parser import command_parser, CommandParser, CommandType
from bot.response_templates import response_templates, ResponseTemplates
from bot.whatsapp_webhook import whatsapp_bot, router as whatsapp_router
from bot.telegram_webhook import telegram_bot, router as telegram_router

__all__ = [
    "command_parser",
    "CommandParser",
    "CommandType",
    "response_templates",
    "ResponseTemplates",
    "whatsapp_bot",
    "whatsapp_router",
    "telegram_bot",
    "telegram_router"
]
