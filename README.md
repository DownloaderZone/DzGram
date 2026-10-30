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
Bot uploads reuse the download connection pool. Bot pacing starts at 128 upload
parts/second and 64 download chunks/second, increases on success, and applies
Telegram flood cooldowns across the transfer's workers. Override the starting
rates with `DZGRAM_BOT_UPLOAD_RATE` and `DZGRAM_BOT_DL_RATE`.
Bot uploads start on the first ready connection and grow the pool in the
background. Slow pool expansion does not delay upload completion. Bot upload
progress callbacks are coalesced to at most ten intermediate reports per second,
with a final completion report.
Downloads request their first chunk on the authorized datacenter API session
while the parallel media pool starts in the background. Enable INFO logging for
`pyrogram.client` to see authorization readiness and first-response timings.
Cold bot uploads can also send their first parts on the existing API connection.
Bot downloads continue on that connection if media pool setup is slow, then add
media workers when those connections are ready. Bot rates ramp up by 16 upload
parts/sec or 8 download chunks/sec per successful second, with flood backoff.
Upload workers join as individual media connections become ready and stay active
until queued parts are acknowledged. CDN downloads reuse Telegram's supplied
hashes rather than fetching hashes again for every chunk.
Bot uploads use four in-flight workers per connection by default; tune this with
`DZGRAM_BOT_UPLOAD_WORKERS`. Ready download connections join during pool startup.
Upload chunks use a single-copy serialization fast path preserving the MTProto
wire format. Crypto uses two to four worker threads by default; override this with
`DZGRAM_CRYPTO_WORKERS` when tuning for your server.

Shared media connections allow at most four in-flight RPCs by default
(`DZGRAM_MAX_INFLIGHT_MEDIA`). This keeps simultaneous large uploads from
multiplying unbounded writes on the same socket. A part that exhausts a
connection's retries is resent through another ready pool connection (three
attempts by default, `DZGRAM_UPLOAD_PART_RETRIES`). Worker shutdown is bounded,
so a broken connection cannot leave `save_file()` stuck forever after the error.
The no-progress timeout defaults to 180 seconds and can be adjusted with
`DZGRAM_UPLOAD_STALL_TIMEOUT`.

Flood waits are logged (`Upload flood wait ...`) together with the current adaptive
rate, and every upload logs a summary (bytes, duration, MiB/s, final rate) at
WARNING when floods occurred or DEBUG otherwise. The pacer is tunable per account
class with `DZGRAM_*_UPLOAD_FLOOR` and `DZGRAM_*_UPLOAD_STEP` (bot, premium, user),
plus shared `DZGRAM_UPLOAD_BACKOFF` (rate multiplier per flood, default 0.85) and
`DZGRAM_UPLOAD_RECOVER` (seconds between successful-part rate increases, default
0.5). A floor of 1 part/s is only ~0.5 MiB/s, so keep the floor at a sane
throughput (defaults: 8 parts/s for bots, 4 for users) rather than 1.

`AUTH_KEY_UNREGISTERED` on an existing user session means its saved authorization
is no longer recognized by Telegram. Generate a new user session string and
replace `USER_SESSION_STRING` in the application's saved configuration (including
MongoDB when it overrides environment settings). Updating server RSA public keys
cannot restore a revoked authorization. The bot must also have access to configured
private chats; numeric chat IDs can be supplied as signed strings or integers.

To compare client transfer performance on the same server, run `benchmark_transfer.py`
in each library's environment with the same bot and file. Set `DZGRAM_API_ID`,
`DZGRAM_API_HASH`, and `DZGRAM_BOT_TOKEN` through environment variables, then run:

```bash
python benchmark_transfer.py --chat -1001234567890 --message 42 --runs 2
python benchmark_transfer.py --upload /path/to/file --runs 2
```

The JSON results separate first-progress latency, total time, and throughput
after first progress; the second run measures warm connections. Upload tests
upload file parts without posting a chat message. Progress callbacks only record
timings, so Telegram status edits do not affect the comparison.

Connection counts can be tuned before starting your client:

| Account | Upload pool | Download pool | Download workers per connection |
| --- | --- | --- | --- |
| User | `DZGRAM_UPLOAD_POOL` (12) | `DZGRAM_DL_POOL` (5) | `DZGRAM_DL_WORKERS` (3) |
| Bot | `DZGRAM_BOT_UPLOAD_POOL` (8) | `DZGRAM_BOT_DL_POOL` (5) | `DZGRAM_BOT_DL_WORKERS` (3) |
| Premium | `DZGRAM_PREMIUM_UPLOAD_POOL` (14) | `DZGRAM_PREMIUM_DL_POOL` (6) | `DZGRAM_PREMIUM_DL_WORKERS` (4) |

### API layer

DzGram 2.3.38 targets Telegram layer 233. The update adds the layer 233 schema
(agent providers, feeds, widgets, hidden user statuses and news channels) plus
high-level wrappers for the new agent, feed, widget, stats, folder and contact
card RPCs.

It also validates and normalises local photo uploads, converting unsupported
image formats (for example GIF) and heavy lossless PNGs to JPEG when Pillow is
available (installed with `dzgram[fast]`), fixing extensions such as
`.jpe`/`.jfif` that Telegram refuses as photos, and capping oversized images the
way the official clients do. Animated GIFs should still be sent with
`send_animation`, which keeps them animated.

### Resources

- Check out [the docs](https://downloaderzone.github.io/DzGram/) (source in [`docs/`](docs/)) to learn more about
DzGram, get started right away and discover more in-depth material for building your client applications. Build them
locally with `cd docs && make html`.
- Join the official [channel](https://t.me/DZGramByDzone) and stay tuned for news, updates and announcements.
- Get help and discuss in the [support group](https://t.me/DzgramDiscussion).
