import discord
from config import FOOTER_TEXT

def build_checkout_embed(x):
    failed = x.status == "failed"
    title = f"❌ Order Canceled: {x.cancel_reason}" if failed else "✅ Successful Checkout"
    e = discord.Embed(title=title,
        color=discord.Color.red() if failed else discord.Color.green())
    e.add_field(name="Item", value=x.item, inline=False)
    e.add_field(name="Price", value=x.price, inline=True)
    e.add_field(name="Site", value=x.site, inline=True)
    e.add_field(name="Quantity", value=x.quantity, inline=True)
    e.add_field(name="Profile", value=x.profile, inline=True)
    if failed:
        e.add_field(name="Cancel Reason", value=x.cancel_reason, inline=True)
    if x.image_url:
        e.set_thumbnail(url=x.image_url)
    e.set_footer(text=FOOTER_TEXT)
    return e
