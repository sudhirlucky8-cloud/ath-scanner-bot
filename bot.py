from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot working ✅\n\nATH Scanner yahan run hoga."
    )

app = ApplicationBuilder().token(
    "8994080718:AAGvFEESkhLgsXjW-_n7x87O4Z1DXoTt_3s"
).build()

app.add_handler(CommandHandler("scan", scan))

print("Bot Started...")

app.run_polling()
