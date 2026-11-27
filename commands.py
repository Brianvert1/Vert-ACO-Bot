import discord
from config import FAILED_CHANNEL_ID, SUCCESS_CHANNEL_ID
from database import get_profile_links, remove_profile_link, set_profile_link
from embeds import build_checkout_embed
from models import Checkout
from pings import get_ping

def is_admin(message):
    return isinstance(message.author, discord.Member) and (
        message.author.guild_permissions.administrator or
        message.author.guild_permissions.manage_guild
    )

async def handle_command(message, client):
    text = message.content.strip()
    low = text.lower()

    if low.startswith("!link"):
        if not is_admin(message):
            await message.channel.send("❌ Administrator or Manage Server permission required.")
            return True
        parts = text.split(maxsplit=2)
        if len(parts) < 3 or not message.mentions:
            await message.channel.send("Usage: `!link keyword @user`")
            return True
        keyword = parts[1]
        user = message.mentions[0]
        set_profile_link(keyword, user.id)
        await message.channel.send(f"✅ Linked **{keyword}** to {user.mention}.")
        return True

    if low.startswith("!unlink"):
        if not is_admin(message):
            await message.channel.send("❌ Administrator or Manage Server permission required.")
            return True
        keyword = text[len("!unlink"):].strip()
        ok = remove_profile_link(keyword) if keyword else False
        await message.channel.send(
            f"✅ Removed **{keyword}**." if ok else "❌ No matching link found."
        )
        return True

    if low == "!links":
        rows = get_profile_links()
        body = "\n".join(f"**{k}** → <@{u}>" for k,u in rows) or "No links saved."
        await message.channel.send("**Saved Profile Links**\n"+body[:1800])
        return True

    if low.startswith("!testfail"):
        profile = text[len("!testfail"):].strip() or "Vert target"
        x = Checkout("failed","Test Product","$24.99","Target","1",profile,"Payment Declined")
        ch = client.get_channel(FAILED_CHANNEL_ID)
        if ch:
            await ch.send(content=get_ping(profile), embed=build_checkout_embed(x),
                          allowed_mentions=discord.AllowedMentions(users=True,roles=False,everyone=False))
        return True

    if low.startswith("!testsuccess"):
        profile = text[len("!testsuccess"):].strip() or "Vert target"
        x = Checkout("success","Test Product","$19.99","Target","1",profile)
        ch = client.get_channel(SUCCESS_CHANNEL_ID)
        if ch:
            await ch.send(content=get_ping(profile), embed=build_checkout_embed(x),
                          allowed_mentions=discord.AllowedMentions(users=True,roles=False,everyone=False))
        return True

    return False
