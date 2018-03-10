from gevent import monkey; monkey.patch_all()
import gevent
import bottle
import telegram
import telegram.ext
import glob
import json
import sys
import re
import argparse

def escapeMarkdown(text):
	escape_chars = '\*_`\['
	return re.sub(r'([%s])' % escape_chars, r'\\\1', text)

class invalidConfigException(Exception):
	pass

try:
	with open("settings.json", "r") as f:
		glob.config = json.loads(f.read())
		if "telegram_token" not in glob.config or "allowed" not in glob.config:
			raise invalidConfigException()
except invalidConfigException:
	print("Invalid settings.json structure")
	sys.exit(-1)
except FileNotFoundError:
	print("settings.json doesn't exist")
	sys.exit(-2)
except json.JSONDecodeError:
	print("Invalid settings.json syntax")
	sys.exit(-3)

# Create telegram bot handlers
def telegramStartHandler(bot, update):
	userID = update.message.from_user.id
	if int(userID) not in glob.config["allowed"]:
		bot.sendMessage(userID, "*Welcome to Ripple Datadog Telegram Bot!*\n_How alert. Such monitoring._\n\nAsk the sysadmin to enable you to use this bot.\n*Your telegram user ID is: {}*".format(userID), parse_mode="markdown")
	else:
		bot.sendMessage(userID, "*You are already allowed to use this bot!*\nYou'll receive alerts from Datadog on this account.", parse_mode="markdown")

# Create telegram bot
updater = telegram.ext.Updater(glob.config["telegram_token"])
updater.dispatcher.add_handler(telegram.ext.CommandHandler("start", telegramStartHandler))
bot = telegram.Bot(glob.config["telegram_token"])

# Start telegram bot in a separate greenlet
gevent.Greenlet(updater.start_polling).start()

# Create bottle handlers
@bottle.post("/")
def apiHandler():
	responseData = {
		"status": 200,
		"message": "ok"
	}
	try:
		data = json.loads(bottle.request.body.read().decode("utf-8"))
		data = dict((k, escapeMarkdown(v)) for k, v in data.items() if v is not None and v != "null")
		data["text_only_msg"] = "\n".join(x for x in data["text_only_msg"].split("\n")[:-1] if x != "")

		message = telegram.Emoji.WARNING_SIGN + " *{event_title}*"
		if "tags" in data:
			message += " - `{tags}`"
		message += "\n"
		if "user" in data:
			message += "(from {user}"
			if "priority" in data:
				message += ", priority: {priority}"
			message += ")"
		message += "\n{text_only_msg}"
		if "snapshot" in data:
			message += "\n\n{snapshot}"

		message = message.format(**data)
		for user in glob.config["allowed"]:
			keyboard = telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton(telegram.Emoji.CHART_WITH_DOWNWARDS_TREND + " View event", url=data["link"])]]) if "link" in data else None
			bot.sendMessage(str(user), message, parse_mode="markdown", reply_markup=keyboard)
	except json.JSONDecodeError:
		responseData["status"] = 400
		responseData["message"] = "Invalid request body syntax"
	finally:
		bottle.response.status = responseData["status"]
		return json.dumps(responseData)

parser = argparse.ArgumentParser(description="Track Datadog updates through Telegram")
parser.add_argument("-p", "--port", dest="port", help="Webserver port", default=9904, type=int)
args = parser.parse_args()

# Start bottle/gevent server
bottle.run(host="0.0.0.0", port=args.port, server="gevent")