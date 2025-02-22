from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import TOKEN
from handlers import start, chat, weather, handle_image  # Import the new function

# Build the application
app = ApplicationBuilder().token(TOKEN).build()

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("weather", weather))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.add_handler(MessageHandler(filters.PHOTO, handle_image))  

# Run the bot
app.run_polling()
