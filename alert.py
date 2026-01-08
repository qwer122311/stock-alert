import yfinance as yf
import requests

# ====== 설정 ======
BOT_TOKEN = "8376732547:AAHFiOcroCr4QzAvK69TDgP3L-629LGHCWM"
CHAT_ID = "7662662191"

TICKERS = {
    "ETN": "이튼",
    "NVDA": "엔비디아",
    "PEP": "펩시코",
    "VRT": "버티브"
}

THRESHOLD = 0.03  # 3%

# ==================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

def check_stock(ticker, name):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="3d")

    if len(hist) < 3:
        return

    close_2d_ago = hist["Close"].iloc[-3]
    close_1d_ago = hist["Close"].iloc[-2]

    change = (close_1d_ago - close_2d_ago) / close_2d_ago

    if abs(change) >= THRESHOLD:
        percent = round(change * 100, 2)
        direction = "상승 📈" if change > 0 else "하락 📉"

        message = (
            f"🔔 {name} ({ticker})\n"
            f"전일 종가 변동: {percent}% {direction}\n\n"
            f"👉 오늘 프리마켓에서 모으기 / 익절 판단"
        )
        send_telegram(message)

def main():
    for ticker, name in TICKERS.items():
        check_stock(ticker, name)

if __name__ == "__main__":
    main()
