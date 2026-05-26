from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import io

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
# SCAN COMMAND
# ==========================================================

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Scanning stocks..."
    )

    # DOWNLOAD DATA
    data = yf.download(

        tickers=stocks,
        period="max",
        interval="1d",
        group_by="ticker",
        progress=False,
        threads=True

    )

    results = []

    # PROCESS
    for stock in stocks:

        try:

            stock_data = data[stock].dropna()

            if stock_data.empty:
                continue

            ath = float(stock_data["High"].max())

            current = float(stock_data["Close"].iloc[-1])

            correction = ((ath - current) / ath) * 100

            if 20 <= correction <= 25:

                results.append({

                    "STOCK": stock.replace(".NS",""),
                    "BELOW ATH": f"{round(correction,2)}%"

                })

        except:
            pass

    # DATAFRAME
    result_df = pd.DataFrame(results)

    if result_df.empty:

        await update.message.reply_text(
            "No stocks found"
        )

        return

    # SORT
    result_df["SORT"] = result_df["BELOW ATH"].str.replace("%","").astype(float)

    result_df = result_df.sort_values(
        by="SORT"
    ).drop(
        columns=["SORT"]
    ).reset_index(drop=True)

    # ==========================================================
    # CREATE IMAGE
    # ==========================================================

    fig_height = max(1, len(result_df) * 0.5)

    fig, ax = plt.subplots(figsize=(8, fig_height))

    ax.axis('off')

    table = ax.table(

        cellText=result_df.values,
        colLabels=result_df.columns,
        loc='center',
        cellLoc='center'

    )

    table.auto_set_font_size(False)

    table.set_fontsize(12)

    table.scale(1.2, 1.5)

    plt.title(

        "ATH Screener Result",
        fontsize=16,
        pad=20

    )

    # SAVE IMAGE IN MEMORY
    buf = io.BytesIO()

    plt.savefig(

        buf,
        format='png',
        bbox_inches='tight',
        dpi=300

    )

    buf.seek(0)

    plt.close()

    # SEND IMAGE
    await update.message.reply_photo(photo=buf)

# ==========================================================
# BOT START
# ==========================================================

app = ApplicationBuilder().token(
    "YAHAN_APNA_BOT_TOKEN_DALO"
).build()

app.add_handler(CommandHandler("scan", scan))

print("Bot Started...")

app.run_polling()
