## ddd
### Track Datadog updates through Telegram

## Requirements
- Python 3.5
- bottle
- gevent
- python-telegram-bot

## Setting up
- Clone the repository
- Install the required dependencies with
```
$ pip install -r requirements.txt
````
- Create a telegram bot through Bot Father
- Put your `telegram_token` in `settings.json`, use `settings.sample.json` as a sample  
- Start `dtg.py`. This will start a bottle webserver on port **9904** and a telegram bot. You can change the port using the `--port` CLI argument. Once the server is started, it'll redirect all the incoming requests that match the Datadog webhook structure to the Telegram API.  
- Log in to Datadog, go in the **Integrations** page, add a **Webhooks** integration
- Give it any name, set the URL to your dtg address (eg: http://1.2.3.4:9904/)
- Tick **Use custom payload** and set **Custom payload** to:
```
{
    "event_title": "$EVENT_TITLE",
    "tags": "$TAGS",
    "user": "$USER",
    "priority": "$PRIORITY",
    "text_only_msg": "$TEXT_ONLY_MSG",
    "snapshot": "$SNAPSHOT",
    "link": "$LINK",
    "alert_query": "$ALERT_QUERY"
}
```
- Untick **Encode as form**, leave **Headers** empty and save the webhook
- Once `dtg.py` is started, go to your Telegram bot and type `/start` to start the bot.
- The bot will tell you your telegram user ID, copy it and add it to the `allowed` array in `settings.json`
- Restart dtg and it'll send all the Datadog updates it receives to all the users inside the `allowed` array in the config file.

## License
MIT