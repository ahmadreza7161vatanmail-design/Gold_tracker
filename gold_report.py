import requests, json
from datetime import datetime

BOT_TOKEN = "8266440766:AAEV7VHtTNv6LCD3VUv9U_bZXBukXAE_kqU"
CHAT_ID = "5617936602"
LAST_VALUE_FILE = "last_gold_qty.json"
API_URL = "https://api.fiscal.treasury.gov/services/api/fiscal_service/v2/accounting/od/gold_reserve"

def fetch_current_gold_qty():
    params = {"fields": "record_date,fine_troy_ounce_qty", "sort": "-record_date", "limit": 1}
    r = requests.get(API_URL, params=params)
    r.raise_for_status()
    data = r.json()["data"][0]
    return {"date": data["record_date"], "qty": float(data["fine_troy_ounce_qty"])}

def load_last_value():
    try:
        with open(LAST_VALUE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_last_value(obj):
    with open(LAST_VALUE_FILE, "w") as f:
        json.dump(obj, f)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def check_gold_change():
    current = fetch_current_gold_qty()
    last = load_last_value()

    if last:
        diff = current["qty"] - last["qty"]
        if diff > 0:
            msg = f"✅ دولت آمریکا طلا خریده است!\nافزایش {diff:,.2f} اونس در تاریخ {current['date']}"
        elif diff < 0:
            msg = f"⚠️ دولت آمریکا طلا فروخته است!\nکاهش {abs(diff):,.2f} اونس در تاریخ {current['date']}"
        else:
            msg = f"ℹ️ بدون تغییر در ذخایر طلا ({current['qty']:,.2f} اونس) تا {current['date']}"
    else:
        msg = f"📊 مقدار اولیه ذخایر طلا: {current['qty']:,.2f} اونس ({current['date']})"

    send_telegram_message(msg)
    save_last_value(current)

if __name__ == "__main__":
    check_gold_change()
