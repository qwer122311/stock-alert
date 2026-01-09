import os
import yfinance as yf
import requests

# ====== 보안 설정 (GitHub Secrets 사용) ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("텔레그램 토큰 또는 CHAT_ID가 설정되지 않았습니다.")

TICKERS = {
    "NVDA": {"name": "엔비디아", "unit": 2},
    "ETN": {"name": "이튼", "unit": 2},
    "VRT": {"name": "버티브", "unit": 3},
}

EXTREME_DROP = -0.08  # -8%

# ==================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def check_stock(ticker, info):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="10d")

    if len(hist) < 7:
        return None

    close_yesterday = hist["Close"].iloc[-2]
    close_day_before = hist["Close"].iloc[-3]

    ma5_yesterday = hist["Close"].iloc[-7:-2].mean()
    ma5_day_before = hist["Close"].iloc[-8:-3].mean()

    # 방향 판단 (2일 연속)
    yesterday_dir = close_yesterday - ma5_yesterday
    before_dir = close_day_before - ma5_day_before

    # 과도 하락 체크
    drop_rate = (close_yesterday - ma5_yesterday) / ma5_yesterday

    if drop_rate <= EXTREME_DROP:
        return (
            f"{ticker} ({info['name']})\n"
            f"→ 하락 과도 구간\n"
            f"👉 모으기 증가 중단 (관망)"
        )

    if yesterday_dir > 0 and before_dir > 0:
        return (
            f"{ticker} ({info['name']})\n"
            f"→ 2일 연속 상승\n"
            f"👉 오늘 모으기 금액 -{info['unit']}달러"
        )

    if yesterday_dir < 0 and before_dir < 0:
        return (
            f"{ticker} ({info['name']})\n"
            f"→ 2일 연속 하락\n"
            f"👉 오늘 모으기 금액 +{info['unit']}달러"
        )

    return (
        f"{ticker} ({info['name']})\n"
        f"→ 변동 없음\n"
        f"👉 오늘 조정 없음"
    )

def main():
    messages = []

    for ticker, info in TICKERS.items():
        msg = check_stock(ticker, info)
        if msg:
            messages.append(msg)

    final_message = "📊 전일 마감 기준 행동 알림 (한국 10:00)\n\n" + "\n\n".join(messages)
    send_telegram(final_message)

if __name__ == "__main__":
    main()
print("BOT_TOKEN:", BOT_TOKEN)
print("CHAT_ID:", CHAT_ID)
