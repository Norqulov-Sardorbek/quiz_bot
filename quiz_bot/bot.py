from quiz_bot.dispatcher import TOKEN
import logging
from requests import post
class TelegramBot:
    HOST = "https://api.telegram.org/bot"

    def __init__(self):
        # Get token from environment variables

        if not TOKEN:
            raise ValueError("Telegram bot TOKEN is missing! Set the TOKEN environment variable.")
        self.base_url = self.HOST + TOKEN

    def send_message(
        self,
        chat_id,
        text,
        reply_markup=None,
        parse_mode="HTML",
    ):
        """
        Sends a message via Telegram Bot API.
        """
        url = self.base_url + "/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }

        # Add reply markup if provided
        if reply_markup:
            data["reply_markup"] = reply_markup.to_json()

        # Send the request
        try:
            res = post(url, json=data)
            res.raise_for_status()  # Raise HTTP errors if they occur
            logging.info(f"Message sent to chat_id {str(chat_id)}: {text}")
            return res.json()
        except Exception as e:
            logging.error(f"Failed to send message to chat_id {str(chat_id)}: {e}")
            return None


# Instantiate the Telegram bot
bot = TelegramBot()