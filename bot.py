import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BOT_TOKEN = "7669087349:AAH9kjk0KZM_NFYh5nC4GYnAcv90aMeCRXI"
CHAT_ID = "421311524"

CATEGORY_URL = "https://www.sheinindia.in/c/sverse-5939-37961"
CHECK_DELAY = 30
DB_FILE = "seen_products.txt"


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium"

    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)


def send_telegram_alert(name, price, link):
    msg = (
        f"<b>🆕 NEW SHEIN ITEM</b>\n\n"
        f"🏷 <b>{name}</b>\n"
        f"💰 <b>{price}</b>\n\n"
        f"👉 <a href='{link}'>View Product</a>"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    })


def load_seen():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE) as f:
        return set(x.strip() for x in f)


def save_seen(link):
    with open(DB_FILE, "a") as f:
        f.write(link + "\n")


def monitor():
    print("🚀 SHEIN Monitor started")

    seen = load_seen()
    first_run = len(seen) == 0

    while True:
        driver = None
        try:
            driver = get_driver()
            driver.get(CATEGORY_URL)

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(5)

            items = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
            print(f"🔍 Found {len(items)} items")

            for item in items:
                link = item.get_attribute("href")
                if not link:
                    continue

                link = link.split("?")[0]
                if link in seen:
                    continue

                seen.add(link)
                save_seen(link)

                if not first_run:
                    text = item.text.split("\n")
                    name = text[0] if text else "New Item"
                    price = "Check link"
                    for t in text:
                        if "₹" in t:
                            price = t

                    send_telegram_alert(name, price, link)

            if first_run:
                print(f"✅ Initialized with {len(seen)} items")
                first_run = False

        except Exception as e:
            print("❌ Error:", e)

        finally:
            if driver:
                driver.quit()

        time.sleep(CHECK_DELAY)


monitor()
