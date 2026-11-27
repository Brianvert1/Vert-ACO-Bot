import re
import discord
from models import Checkout

ALIASES = {
    "item": {"item","product","product name","item name","title"},
    "price": {"price","total","amount","retail","checkout total"},
    "site": {"site","store","retailer","website","merchant"},
    "quantity": {"quantity","qty","count"},
    "profile": {"profile","profile name","task profile","billing profile"},
    "cancel": {"cancel reason","failure reason","decline reason","reason","error","message"},
    "status": {"status","fraud status","checkout status","result"},
}

def norm(v):
    return " ".join((v or "").lower().strip().split())

def get_field(embed, group, default=""):
    for f in embed.fields:
        if norm(f.name) in ALIASES[group]:
            return f.value.strip()
    return default

def all_text(embed):
    return " ".join([embed.title or "", embed.description or "", embed.url or ""] +
                    [f"{f.name} {f.value}" for f in embed.fields])

def detect_status(embed):
    text = norm((embed.title or "")+" "+(embed.description or "")+" "+get_field(embed,"status"))
    failed = ["failed","failure","declined","cancelled","canceled","out of stock","payment error","testing failure webhook"]
    return "failed" if any(x in text for x in failed) else "success"

def detect_site(embed):
    explicit = get_field(embed,"site")
    if explicit:
        return explicit
    text = norm(all_text(embed))
    sites = {
        "Target":["target"], "Walmart":["walmart"],
        "Pokémon Center":["pokemoncenter","pokemon center","pokémon center"],
        "Best Buy":["bestbuy","best buy"], "Amazon":["amazon"],
        "Costco":["costco"], "Sam's Club":["samsclub","sam's club","sams club"],
        "GameStop":["gamestop"], "Nike":["nike"], "Adidas":["adidas"]
    }
    for name, keys in sites.items():
        if any(k in text for k in keys):
            return name
    return "Unknown"

def detect_image(embed):
    if embed.thumbnail and embed.thumbnail.url:
        return embed.thumbnail.url
    if embed.image and embed.image.url:
        return embed.image.url
    return None

def item_price(embed):
    item = get_field(embed,"item","N/A")
    price = get_field(embed,"price")
    if not price:
        m = re.search(r"\s*(?:-|—|\|)\s*(\$\d[\d,]*(?:\.\d{1,2})?)\s*$", item)
        if m:
            price = m.group(1)
            item = item[:m.start()].strip()
    if not price:
        m = re.search(r"\$\d[\d,]*(?:\.\d{1,2})?", all_text(embed))
        if m:
            price = m.group(0)
    return item or "N/A", price or "N/A"

def reason(embed):
    explicit = get_field(embed,"cancel")
    if explicit:
        return explicit
    text = norm((embed.title or "")+" "+(embed.description or ""))
    if "payment declined" in text or "card declined" in text:
        return "Payment Declined"
    if "item demand" in text:
        return "Policy - Item Demand"
    if "out of stock" in text or "sold out" in text:
        return "Out of Stock"
    if "testing failure webhook" in text:
        return "Testing failure webhook"
    return "Unknown"

def parse_checkout(embed):
    item, price = item_price(embed)
    return Checkout(
        status=detect_status(embed),
        item=item,
        price=price,
        site=detect_site(embed),
        quantity=get_field(embed,"quantity","1"),
        profile=get_field(embed,"profile","N/A"),
        cancel_reason=reason(embed),
        image_url=detect_image(embed),
    )
