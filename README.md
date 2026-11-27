# Vert ACO Bot

Discord checkout relay/formatter for Any Bot!

## Features

- Watches raw success and raw failure channels
- Keeps original raw checkout messages
- Sends clean successes to `#aco-checkouts`
- Sends clean failures to `#failed-checkouts`
- Parses Hayha/Refract checkout embeds
- Pings Discord users by profile keyword
- Stores checkout history in SQLite
- Includes `!link`, `!unlink`, `!links`, `!testfail`, and `!testsuccess`

## Setup

```cmd
py -m pip install -r requirements.txt
copy .env.example .env
py bot.py
```

Put your bot token in `.env`:

```env
DISCORD_TOKEN=YOUR_TOKEN
```

Never commit `.env`, webhook URLs, bot tokens, or `data/checkouts.db`.


