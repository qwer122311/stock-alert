import os
import yfinance as yf
import requests

# ===============================
# 🔐 보안: 환경변수에서 불러오기
# ===============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("텔레그램 토큰 또는 CHAT_ID가 설정되지 않았습니다.")

# ===============================
# 📊 종목 설정
# ===============================
TICKERS = {
    "NVDA": {"name": "엔비디아", "delta": 2},
    "ETN": {"name": "이튼", "delta": 2},
    "VRT": {"name": "버티브", "delta": 3},
    "PEP": {"name": "펩시코", "delta": 0},
}

THRESHOLD = 0.01  # ±1%

# ===============================

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

def check_stock(ticker, info):
    data = yf.Ticker(ticker).history(period="10d")

    if len(data) < 6:
        return

    close = data["Close"].iloc[-1]
    ma5 = data["Close"].rolling(5).mean().iloc[-1]

    upper = ma5 * (1 + THRESHOLD)
    lower = ma5 * (1 - THRESHOLD)

    name = info["name"]
    delta = info["delta"]

    if close >= upper:
        if delta > 0:
            action = f"모으기 {delta}달러 축소"
        else:
            action = "추세 강함 (행동 없음)"
        direction = "상승 📈"

    elif close <= lower:
        if delta > 0:
            action = f"모으기 {delta}달러 증가"
        else:
            action = "하락 확인 (행동 없음)"
        direction = "하락 📉"

    else:
        return  # 기준 미충족 시 알림 없음

    message = (
        f"🔔 {name} ({ticker})\n"
        f"어제 종가 기준: {direction}\n\n"
        f"👉 오늘 행동: {action}"
    )

    send_telegram(message)

def main():
    for ticker, info in TICKERS.items():
        check_stock(ticker, info)

if __name__ == "__main__":
    main()
