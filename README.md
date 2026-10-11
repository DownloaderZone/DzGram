<p align="center">
    <a href="https://github.com/DownloaderZone/DzGram">
        <img src="https://raw.githubusercontent.com/pyrogram/artwork/master/artwork/pyrogram-logo.png" alt="DzGram" width="128">
    </a>
    <br>
    <b>Telegram MTProto API Framework for Python</b>
    <br>
    <a href="https://downloaderzone.github.io/DzGram/">
        Documentation
    </a>
    •
    <a href="https://github.com/DownloaderZone/DzGram/releases">
        Releases
    </a>
    •
    <a href="https://t.me/DZGramByDzone">
        Channel
    </a>
    •
    <a href="https://t.me/DzgramDiscussion">
        Support
    </a>
</p>

## DzGram

> Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots

``` python
from pyrogram import Client, filters

app = Client("my_account")


@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from Pyrogram!")


app.run()
```

**DzGram** is a modern, elegant and asynchronous [MTProto API](https://github.com/DownloaderZone/DzGram)
framework. It enables you to easily interact with the main Telegram API through a user account (custom client) or a bot
identity (bot API alternative) using Python.

### Key Features

- **Ready**: Install DzGram with pip and start building your applications right away.
- **Easy**: Makes the Telegram API simple and intuitive, while still allowing advanced usages.
- **Elegant**: Low-level details are abstracted and re-presented in a more convenient way.
- **Fast**: Boosted up by [WarpCrypto](https://github.com/rjriajul/WarpCrypto), a high-performance cryptography library written in Rust.  
- **Type-hinted**: Types and methods are all type-hinted, enabling excellent editor support.
- **Async**: Fully asynchronous (also usable synchronously if wanted, for convenience).
- **Powerful**: Full access to Telegram's API to execute any official client action and more.

### Installing

``` bash
pip3 install dzgram
```

### Transfer performance

Uploads use reusable, size-capped connection pools and burst dispatch. User and
bot transfers adapt their request rate on successful parts and Telegram flood
waits; Premium transfers skip client-side pacing while still respecting flood
waits. Progress callbacks are called when the completed byte count changes.
Bot and Premium downloads prefetch the first parallel wave while the initial chunk is
in flight. Transfer connections use Telegram's advertised media endpoints, and
TCP receive buffers assemble fragmented packets without repeatedly copying them.
Bot uploads reuse the download connection pool. Bot pacing starts at 32 upload
parts/second and 16 download chunks/second, increases on success, and applies
Telegram flood cooldowns across the transfer's workers. Override the starting
rates with `DZGRAM_BOT_UPLOAD_RATE` and `DZGRAM_BOT_DL_RATE`.

Connection counts can be tuned before starting your client:

| Account | Upload pool | Download pool | Download workers per connection |
| --- | --- | --- | --- |
| User | `DZGRAM_UPLOAD_POOL` (12) | `DZGRAM_DL_POOL` (5) | `DZGRAM_DL_WORKERS` (3) |
| Bot | `DZGRAM_BOT_UPLOAD_POOL` (8) | `DZGRAM_BOT_DL_POOL` (5) | `DZGRAM_BOT_DL_WORKERS` (3) |
| Premium | `DZGRAM_PREMIUM_UPLOAD_POOL` (14) | `DZGRAM_PREMIUM_DL_POOL` (6) | `DZGRAM_PREMIUM_DL_WORKERS` (4) |

### Resources

- Check out [the docs](https://downloaderzone.github.io/DzGram/) (source in [`docs/`](docs/)) to learn more about
DzGram, get started right away and discover more in-depth material for building your client applications. Build them
locally with `cd docs && make html`.
- Join the official [channel](https://t.me/DZGramByDzone) and stay tuned for news, updates and announcements.
- Get help and discuss in the [support group](https://t.me/DzgramDiscussion).
