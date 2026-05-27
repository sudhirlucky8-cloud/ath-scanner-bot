async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Scanning stocks...")

    results = []

    try:
        data = yf.download(
            tickers=" ".join(stocks),
            period="5y",
            interval="1d",
            group_by="ticker",
            threads=False,   # IMPORTANT FIX
            progress=False
        )
    except Exception as e:
        await update.message.reply_text(f"Download error: {e}")
        return

    for stock in stocks:

        try:
            if stock not in data.columns.get_level_values(0):
                continue

            df = data[stock].dropna()

            if df.empty:
                continue

            ath = df["High"].max()
            current = df["Close"].iloc[-1]

            correction = ((ath - current) / ath) * 100

            if 20 <= correction <= 25:
                results.append({
                    "STOCK": stock.replace(".NS",""),
                    "BELOW ATH": f"{round(correction,2)}%"
                })

        except Exception as e:
            print(stock, e)
            continue

    if not results:
        await update.message.reply_text("No stocks found")
        return

    df_result = pd.DataFrame(results)

    df_result["SORT"] = df_result["BELOW ATH"].str.replace("%","").astype(float)
    df_result = df_result.sort_values("SORT").drop(columns=["SORT"]).reset_index(drop=True)

    fig_height = max(2, len(df_result) * 0.6)

    fig, ax = plt.subplots(figsize=(8, fig_height))
    ax.axis("off")

    ax.table(
        cellText=df_result.values,
        colLabels=df_result.columns,
        loc="center",
        cellLoc="center"
    )

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    buf.seek(0)
    plt.close()

    await update.message.reply_photo(photo=buf)
