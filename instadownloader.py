import requests
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import os

# Telegram bot token received from BotFather
TOKEN = "your_telegram_bot_token"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to the Instagram video downloader bot! Send me the Instagram video link.")

# Function to handle the message containing the Instagram video link
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text.strip()
    modified_url = modify_instagram_link(url)
    if not modified_url:
        await update.message.reply_text("Invalid Instagram video link. Please make sure the link is correct.")
        return

    video_url = await fetch_instagram_video_url(modified_url)
    if video_url:
        video_path = await download_video_file(video_url)
        if video_path:
            await update.message.reply_text("Video downloaded successfully.")
            os.remove(video_path)  # Clean up by removing the downloaded file
        else:
            await update.message.reply_text("Sorry, couldn't download the video. Please try again later.")
    else:
        await update.message.reply_text("Sorry, couldn't fetch the video. Make sure the link is correct or try again later.")

# Function to modify the Instagram link to ensure it can retrieve JSON data
def modify_instagram_link(url: str) -> str:
    # Check if the link already contains "?__a=1"
    if "?__a=1" in url:
        return url
    # Add "?__a=1" to the end of the link
    elif url.endswith("/"):
        return f"{url}?__a=1"
    else:
        return f"{url}/?__a=1"

# Function to fetch the Instagram video URL
async def fetch_instagram_video_url(instagram_url: str) -> str:
    try:
        response = requests.get(instagram_url)
        if response.status_code == 200:
            json_data = response.json()
            video_url = json_data['graphql']['shortcode_media']['video_url']
            return video_url
        else:
            logger.error(f"Error fetching video URL: Status code {response.status_code}")
    except Exception as e:
        logger.error(f"Exception occurred while fetching video URL: {e}")
    return None

# Function to download the video file from the video URL
async def download_video_file(video_url: str) -> str:
    try:
        video_path = "downloaded_video.mp4"
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(video_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return video_path
    except Exception as e:
        logger.error(f"Error downloading video file: {e}")
    return None

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - handle the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    # Run the bot until you press Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
