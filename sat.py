import asyncio

import sqlite3

import nextcord
import os

from discord.ext import tasks, commands
from dotenv import load_dotenv

load_dotenv()

db = sqlite3.connect('database.db')
sql = db.cursor()


async def get_prefix(client, message):
    sql.execute('SELECT prefix FROM prefixes WHERE guild = ?', (message.guild.id,))
    data = sql.fetchone()
    if data:
        return commands.when_mentioned_or(*data)(client, message)
    else:
        try:
            sql.execute('INSERT INTO prefixes (prefix, guild) VALUES (?, ?)', ('!', message.guild.id,))
            sql.execute('SELECT prefix FROM prefixes WHERE guild = ?', (message.guild.id,))
            data = sql.fetchone()
            if data:
                sql.execute('UPDATE prefixes SET prefix = ? WHERE guild = ? ', ('!', message.guild.id,))
        except Exception:
            return commands.when_mentioned_or('!')(client, message)


activity = nextcord.Activity(name=f'Minecraft', type=nextcord.ActivityType.playing)
intents = nextcord.Intents.all()
bot = commands.Bot(
    command_prefix=get_prefix,
    description='Бот, которому нужны ваши пальцы ног',
    intents=intents,
    activity=activity
)


@bot.event
async def on_ready():
    print(f'Бот {bot.user} готов')
    sql.execute("""CREATE TABLE IF NOT EXISTS prefixes (
        prefix TEXT,
        guild ID
    )""")
    db.commit()


@bot.event
async def on_ready():
    sql.execute("""CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        id ID,
        xp INT
    )""")
    db.commit()


@bot.event
async def on_guild_join(guild):
    sql.execute('INSERT INTO prefixes (prefix, guild) VALUES (?, ?)', ('!', guild.id,))
    db.commit()


@bot.event
async def on_guild_remove(guild):
    sql.execute('SELECT prefix FROM prefixes WHERE guild = ?', (guild.id,))
    data = sql.fetchone()
    if data:
        sql.execute('DELETE FROM prefixes WHERE guild = ?', (guild.id,))
    db.commit()


@bot.command()
async def setprefix(ctx, prefix=None):
    await ctx.channel.purge()
    if prefix is None:
        return
    sql.execute('SELECT prefix FROM prefixes WHERE guild = ?', (ctx.guild.id,))
    data = sql.fetchone()
    if not data:
        sql.execute('INSERT INTO prefixes (prefix, guild) VALUES (?, ?)', ('!', ctx.guild.id,))
        sql.execute('SELECT prefix FROM prefixes WHERE guild = ?', (ctx.guild.id,))
        data = sql.fetchone()
        if data:
            sql.execute('UPDATE prefixes SET prefix = ? WHERE guild = ? ', (prefix, ctx.guild.id,))
            await ctx.send(f"Префикс изменен '{prefix}'")
        else:
            return
    else:
        sql.execute('UPDATE prefixes SET prefix = ? WHERE guild = ? ', (prefix, ctx.guild.id,))
        await ctx.send(f"Префикс изменен `{prefix}`")
    db.commit()


for cog_name in os.listdir("./module"):
    if cog_name.endswith(".py"):
        bot.load_extension(f"module.{cog_name[:-3]}")
        print(f"Модуль {cog_name[:-3].upper()} загружен!")

bot.run(os.getenv("TOKEN"))
