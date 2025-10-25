from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time, os

# === CONFIG === --- UPDATE WITH YOUR USERNAME ---
CHROME_USER_DATA = r"C:\Users\YOUR_USERNAME\AppData\Local\Google\Chrome\User Data"
PROFILE_DIR = "Default"
TEMP_WRAPPER = os.path.join(os.getenv("TEMP"), "chrome_selenium_wrapper")
os.makedirs(TEMP_WRAPPER, exist_ok=True)

# === CHROME OPTIONS ===
opts = Options()
opts.add_argument(f"--user-data-dir={TEMP_WRAPPER}")
opts.add_argument(f"--profile-directory={PROFILE_DIR}")
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_argument("--start-maximized")
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_experimental_option("useAutomationExtension", False)

print("🚀 Starting Chrome…")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
wait = WebDriverWait(driver, 20)

# === UTILS ===
def js_click(el):
    driver.execute_script("arguments[0].click();", el)

def try_click_xpath(xpath, timeout=5, label="element"):
    """Waits for element by xpath and clicks if found"""
    try:
        el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        js_click(el)
        print(f"✅ Clicked {label}")
        return True
    except Exception:
        print(f"⚠️ {label} not found or not clickable (skipped)")
        return False

def ensure_logged_out():
    """If Sign in not found, attempt logout via profile avatar"""
    print("🧭 Checking if already logged in...")
    sign_in_found = False
    try:
        driver.find_element(By.XPATH, "//span[normalize-space()='Sign in']")
        sign_in_found = True
    except:
        pass

    if not sign_in_found:
        print("⚠️ Sign in not found — probably logged in, attempting logout...")
        avatar_xpath = (
            "//button[contains(@aria-haspopup,'true') "
            "and contains(@class,'rounded-full') "
            "and (descendant::img or descendant::div[contains(@class,'bg-gradient')])]"
        )
        avatar_clicked = try_click_xpath(avatar_xpath, 10, "profile avatar (pre-logout)")
        if avatar_clicked:
            time.sleep(1)
            try_click_xpath("//div[normalize-space()='Log out']", 10, "Log out (pre-login cleanup)")
            print("✅ Logged out previous account.")
            time.sleep(1)  # allow UI to update
        else:
            print("⚠️ Could not find avatar to log out; continuing anyway.")
    else:
        print("🟢 'Sign in' button visible — not logged in, continuing normally.")

# === READ ACCOUNTS ===
df = pd.read_excel("AccountList.xlsx")
print(f"Found {len(df)} accounts in AccountList.xlsx")

# === LOOP ACCOUNTS ===
for i, row in df.iterrows():
    email = str(row["Accounts"]).strip()
    pwd = str(row["Passwords"]).strip()
    print(f"\n==============================")
    print(f"🔹 Processing account {i+1}/{len(df)}: {email}")
    print("==============================")

    # 1️⃣ Open PixAI
    driver.get("https://pixai.art/en")
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception:
        print("❌ Failed to load PixAI page.")
        continue

    # 1.5️⃣ Ensure logged out before logging in
    ensure_logged_out()

    # 2️⃣ Click Sign in → Continue with Email
    try_click_xpath("//span[normalize-space()='Sign in']", 15, "Sign in")
    try_click_xpath("//span[contains(normalize-space(),'Continue with Email')]", 15, "Continue with Email")

    # 3️⃣ Fill credentials and log in
    try:
        email_in = wait.until(EC.presence_of_element_located((By.ID, "email-input")))
        email_in.clear()
        email_in.send_keys(email)

        pwd_in = driver.find_element(By.ID, "password-input")
        pwd_in.clear()
        pwd_in.send_keys(pwd)

        js_click(driver.find_element(By.XPATH, "//span[normalize-space()='Login']"))
        print("✅ Submitted login form.")
    except Exception as e:
        print(f"❌ Failed to log in: {e}")
        continue

    # 4️⃣ Check for daily credit popup (max 5 s)
    print("⏳ Checking for daily claim popup (5 s)…")
    claimed = try_click_xpath("//span[contains(normalize-space(),'Claim 10')]", 5, "daily credit claim")
    if claimed:
        print("🎉 Claimed daily credits — closing popup…")
        closed = try_click_xpath("//span[normalize-space()='Close']", 5, "Close popup")
        if closed:
            print("✅ Popup closed.")
        else:
            print("⚠️ Could not find 'Close' button (maybe auto-closed).")
    else:
        print("No claim popup (likely already claimed).")

    # 5️⃣ Log out
    print("⏳ Logging out…")
    time.sleep(3)

    avatar_xpath = (
        "//button[contains(@aria-haspopup,'true') "
        "and contains(@class,'rounded-full') "
        "and (descendant::img or descendant::div[contains(@class,'bg-gradient')])]"
    )

    avatar_clicked = try_click_xpath(avatar_xpath, 10, "profile avatar")
    if avatar_clicked:
        time.sleep(1)
        try_click_xpath("//div[normalize-space()='Log out']", 10, "Log out")
        print(f"✅ Logged out {email}")
        time.sleep(1)  # allow UI to update before next account
    else:
        print("⚠️ Could not find profile icon for logout.")

    time.sleep(3)

print("\n✅ All accounts processed. Closing Chrome…")
driver.quit()
print("🧹 Driver closed successfully.")
