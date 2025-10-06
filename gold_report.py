import os
import requests
import json

# دریافت مقادیر از Secrets GitHub Actions
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN و CHAT_ID باید در Secrets تنظیم شوند.")

API_URL = "https://api.fiscal.treasury.gov/services/api/fiscal_service/v2/accounting/od/gold_reserve"
LAST_VALUE_FILE = "last_gold_qty.json"

def fetch_latest_two():
    try:
        params = {"fields":"record_date,fine_troy_ounce_qty","sort":"-record_date","limit":2}
        r = requests.get(API_URL, params=params, timeout=30)
        r.raise_for_status()
        data = r.json().get("data", [])
        if not data:
            raise ValueError("هیچ داده‌ای از API دریافت نشد.")
        return data
    except Exception as e:
        raise RuntimeError(f"خطا در دریافت داده از API: {e}")

def build_message(data):
    cur = data[0]
    cur_date = cur["record_date"]
    cur_qty = float(cur["fine_troy_ounce_qty"])
    if len(data) > 1:
        prev = data[1]
        prev_date = prev["record_date"]
        prev_qty = float(prev["fine_troy_ounce_qty"])
        diff = cur_qty - prev_qty
        if diff > 0:
            return f"✅ دولت آمریکا طلا خریده\nافزایش {diff:,.2f} اونس\nتا تاریخ {cur_date} (مقایسه با {prev_date})"
        elif diff < 0:
            return f"⚠️ دولت آمریکا طلا فروخته\nکاهش {abs(diff):,.2f} اونس\nتا تاریخ {cur_date} (مقایسه با {prev_date})"
        else:
            return f"ℹ️ بدون تغییر: {cur_qty:,.2f} اونس تا تاریخ {cur_date} (مقایسه با {prev_date})"
    else:
        return f"📊 مقدار فعلی: {cur_qty:,.2f} اونس تا تاریخ {cur_date}"

def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"ارسال پیام به تلگرام موفق نبود: {resp.text}")

def main():
    data = fetch_latest_two()
    msg = build_message(data)
    send_telegram_message(BOT_TOKEN, CHAT_ID, msg)
    print("پیام با موفقیت ارسال شد ✅")

if __name__ == "__main__":
    main()
