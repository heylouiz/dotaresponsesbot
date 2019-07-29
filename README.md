# @Dotaresponsesbot

A Telegram bot written in Python that sends voice messages from Dota 2.

Check it out: www.telegram.me/dotaresponsesbot
You can use it in any chat, try to use it by typing the command bellow and wait for the sounds to appear:
```
@dotaresponsesbot first blood
```

## Installing dependencies and running

Note: Before start you need to create a telegram bot and get a token, check the oficial documentation here:

https://core.telegram.org/bots

### Run with Docker (Recommended)

To run this bot using Docker

```
docker build -t dotaresponsesbot .

docker run -t --name dotaresponsesbot \
              -e TELEGRAM_TOKEN='' \
              dotaresponsesbot
```

Note: TELEGRAM_TOKEN='' needs to be replaced with your bot's token.

#### Run without Docker

##### Install Dependencies

Create a virtualenv (Optional):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the requirements (if you are in a virtualenv, "sudo" is not necessary):
```bash
sudo pip install -r requirements.txt
```

Running:

After all the requirements are installed you can run the bot using the command:
```bash
TELEGRAM_TOKEN=<YOUR BOT'S TOKEN> python dotaresponsesbot.py
```


If you have any questions let me know!
