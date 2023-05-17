from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("/cal", "TOMB PEG Info"),
        types.BotCommand("/bcal", "BASED PEG Info"),
        types.BotCommand("/tip", "Support dev"),
    ])
