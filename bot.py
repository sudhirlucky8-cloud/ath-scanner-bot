from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import io
import time

# ==========================================================
# STOCK LIST
# ==========================================================

stocks = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS",
    "ICICIBANK.NS","INFY.NS","ITC.NS",
    "SBIN.NS","BHARTIARTL.NS","LT.NS",
    "KOTAKBANK.NS","AXISBANK.NS",
    "HAL.NS","TRENT.NS","DMART.NS",
    "SIEMENS.NS","DLF.NS"
]

# ==========================================================
# SCAN COMMAND (FIXED)
# ==========================================================

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Scanning stocks...")

    results = []

    # PROCESS EACH STOCK SAFELY (NO DATA LOSS)
    for stock in stocks:

        try:
            time.sleep(0.1)  # avoid rate limit

            df = yf.Ticker(stock).history(period="5y", interval="1d")

            if df is None or df.empty:
                continue

            ath = float(df["High"].max())
            current = float(df["Close"].iloc[-1])

            correction = ((ath - current) / ath) * 100

            if 20 <= correction <= 25:
                results.append({
                    "STOCK": stock.replace(".NS", ""),
                    "BELOW ATH": f"{round(correction, 2)}%"
                })

        except Exception as e:
            print(stock, "error:", e)
            continue

    # ==========================================================
    # RESULT CHECK
    # ==========================================================

    if len(results) == 0:
        await update.message.reply_text("No stocks found")
        return

    df_result = pd.DataFrame(results)

    df_result["SORT"] = df_result["BELOW ATH"].str.replace("%", "").astype(float)
    df_result = df_result.sort_values("SORT").drop(columns=["SORT"]).reset_index(drop=True)

    # ==========================================================
    # CREATE IMAGE
    # ==========================================================

    fig_height = max(2, len(df_result) * 0.6)

    fig, ax = plt.subplots(figsize=(8, fig_height))
    ax.axis("off")

    table = ax.table(
        cellText=df_result.values,
        colLabels=df_result.columns,
        loc="center",
        cellLoc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)

    plt.title("ATH Screener Result", fontsize=16, pad=20)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    buf.seek(0)
    plt.close()

    await update.message.reply_photo(photo=buf)


# ==========================================================
# BOT START
# ==========================================================

app = ApplicationBuilder().token(
    "YOUR_BOT_TOKEN_HERE"
).build()

app.add_handler(CommandHandler("scan", scan))

print("Bot Started...")

app.run_polling()
