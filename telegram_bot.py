import sys
import os
import io
from ohlc_sitcom import *
from chart_generator import CustomCandlestick, scale_ohlc_data
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
# Ensure the directory of chart_generator.py is in the Python path
# If both files are in the same folder, this is usually unnecessary,
# but good practice if you start structuring it into packages later.
# try:
#     from chart_generator import CustomCandlestick, scale_ohlc_data, get_mock_ohlc_data
# except ImportError:
#     print("Error: Could not import chart_generator module. Make sure 'chart_generator.py' is in the same directory.")
#     sys.exit(1)


# --- Telegram Bot Imports ---
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- Configuration ---
# !!! REPLACE THIS WITH YOUR ACTUAL TELEGRAM BOT TOKEN !!!
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CG_KEY = os.environ.get('CG_KEY')

# ----------------------------------------------------------------------
# --- Telegram Bot Handlers --------------------------------------------
# ----------------------------------------------------------------------

def generate_buttons():
    # 1. Define the button structure
    button_list = [
    [
        InlineKeyboardButton("🔗 Website", url="https://degenerative-sitcom.online/"),
        InlineKeyboardButton("🛒 Buy", url="https://raydium.io/swap/?inputMint=sol&outputMint=AK9yVoXKK1Cjww7HDyjYNyW5FujD3FJ2xbjMUStspump")
    ]
    # You can add more rows of buttons here if needed
    # [InlineKeyboardButton("Another Row Button", callback_data="another_action")]
    ]
    # This creates a single row with one button that links to Google.
    # 2. Create the markup object
    reply_markup = InlineKeyboardMarkup(button_list)
    return reply_markup

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text(
        "Welcome! Use the /chart command to get a generated candlestick chart. 🚀"
    )

async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /chart command, generates, and sends the chart."""
    chat_id = update.effective_chat.id
    print(chat_id)
    # await context.bot.send_message(chat_id=chat_id, text="Generating chart... 📊")

    try:
        # 1. GET DATA (Using the imported mock data function)
        original_data = get_ohlc(coin_id = 'degenerative-sitcom',cg_key=CG_KEY)

        volume_mcap_data = get_coin_data(coin_id = 'degenerative-sitcom',cg_key=CG_KEY)

        scale_factor = 1_000_000_000
        scaled_data = scale_ohlc_data(original_data, scale_factor)

        # 2. CREATE AND PLOT CHART using the imported class
        chart = CustomCandlestick(scaled_data, graphic='triangle', width=0.4)
        chart.plot(
            title="",
            xlabel="Time",
            ylabel="Mcap"
        )

        # 3. SAVE CHART TO MEMORY BUFFER
        photo_buffer = chart.get_image_buffer()

        # 4. SEND CHART
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo_buffer,
            caption = volume_mcap_data,
            parse_mode = 'HTML',
            reply_markup=generate_buttons()
        )

    except Exception as e:
        print(f"Error generating or sending chart: {e}")


def main():
    """Starts the bot."""
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("!!! ERROR: Please replace 'YOUR_TELEGRAM_BOT_TOKEN_HERE' with your actual bot token. !!!")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    # app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("chart", chart_command))

    print("Bot is running... Press Ctrl-C to stop.")
    app.run_polling(poll_interval=1.0)


if __name__ == "__main__":
    main()