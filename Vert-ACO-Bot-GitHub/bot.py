import os
import discord
from dotenv import load_dotenv

from commands import handle_command
from config import FAILED_CHANNEL_ID, KEEP_RAW_MESSAGES, RAW_CHECKOUT_CHANNEL_IDS, SUCCESS_CHANNEL_ID
from database import initialize_database, save_checkout
from embeds import build_checkout_embed
from parser import parse_checkout
from pings import get_ping

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    initialize_database()
    print(f"Logged in as {client.user}")
    print("Watching Hayha and Refract checkouts...")
    print(f"Raw channel IDs: {RAW_CHECKOUT_CHANNEL_IDS}")
    print(f"Success channel ID: {SUCCESS_CHANNEL_ID}")
    print(f"Failed channel ID: {FAILED_CHANNEL_ID}")

@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return

    if message.content:
        try:
            if await handle_command(message, client):
                return
        except Exception as error:
            print(f"[COMMAND ERROR] {error}")

    if message.channel.id not in RAW_CHECKOUT_CHANNEL_IDS or not message.embeds:
        return

    for source in message.embeds:
        try:
            checkout = parse_checkout(source)
        except Exception as error:
            print(f"[PARSER ERROR] {error}")
            continue

        channel_id = FAILED_CHANNEL_ID if checkout.status == "failed" else SUCCESS_CHANNEL_ID
        channel = client.get_channel(channel_id)

        if channel is None:
            print(f"Could not find destination channel {channel_id}")
            continue

        try:
            await channel.send(
                content=get_ping(checkout.profile),
                embed=build_checkout_embed(checkout),
                allowed_mentions=discord.AllowedMentions(users=True,roles=False,everyone=False),
            )
            save_checkout(checkout)
            print(f"Posted {checkout.status} checkout for {checkout.profile} at {checkout.site}")
        except discord.Forbidden:
            print(f"Missing permissions in channel {channel_id}")
        except discord.HTTPException as error:
            print(f"Discord send error: {error}")

    if not KEEP_RAW_MESSAGES:
        try:
            await message.delete()
        except discord.Forbidden:
            print("Missing Manage Messages permission.")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing from .env")

client.run(TOKEN)
