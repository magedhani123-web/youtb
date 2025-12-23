import time
import random
import os
from stem import Signal
from stem.control import Controller
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

# --- إعدادات البوت ---
VIDEO_URL = "https://youtube.com/shorts/MrKhyV4Gcog"
TOTAL_VIEWS = 100
MAX_WORKERS = 1  # يفضل 1 في البداية عند استخدام xvfb لتقليل الضغط
TOR_CONTROL_PORT = 9051
TOR_PASSWORD = "123456"

# --- قائمة الأجهزة (User-Agents) لتضليل يوتيوب ---
USER_AGENTS = [
    # Windows 10
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Android Mobile (Samsung)
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    # Linux Desktop
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # iPhone 14
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    # macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"
]

def change_tor_ip():
    """طلب هوية جديدة من شبكة Tor"""
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            controller.authenticate(password=TOR_PASSWORD)
            controller.signal(Signal.NEWNYM)
        print("🔄 [Tor] جاري تغيير الـ IP... (انتظار 8 ثوانٍ)")
        time.sleep(8)
    except Exception as e:
        print(f"⚠️ فشل تغيير IP (تأكد أن Tor يعمل): {e}")

def get_driver():
    """تجهيز متصفح ببصمة جهاز مختلفة في كل مرة"""
    ua = random.choice(USER_AGENTS)
    options = uc.ChromeOptions()
    options.add_argument(f'--user-agent={ua}')
    options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
    options.add_argument("--mute-audio")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1280,720')
    
    # تحسين التخفي
    options.add_argument("--disable-blink-features=AutomationControlled")

    try:
        # ملاحظة: أزلنا version_main ليقوم السكربت باكتشاف النسخة تلقائياً وتجنب الأخطاء
        driver = uc.Chrome(options=options, use_subprocess=True)
        print(f"📱 الجهاز المختار: {ua[:40]}...")
        return driver
    except Exception as e:
        print(f"❌ خطأ في فتح المتصفح: {e}")
        return None

def run_session(view_index):
    """جلسة المشاهدة الكاملة"""
    change_tor_ip()
    driver = get_driver()
    if not driver: return

    try:
        wait = WebDriverWait(driver, 25)
        print(f"🚀 [View {view_index}] الدخول للرابط...")
        driver.get(VIDEO_URL)
        time.sleep(5)

        # 1. التقاط صورة أولية (للتشخيص)
        # driver.save_screenshot(f"debug_start_{view_index}.png")

        # 2. التعامل مع نافذة الكوكيز (Accept all)
        try:
            accept_btn = driver.find_elements(By.XPATH, "//button[contains(., 'Accept') or contains(., 'agree') or contains(., 'وافق')]")
            if accept_btn:
                accept_btn[0].click()
                print("✅ [Cookie] تم قبول ملفات التعريف")
                time.sleep(2)
        except: pass

        # 3. فحص كشف البوت (Sign in to confirm)
        if "confirm you’re not a bot" in driver.page_source:
            print(f"🚫 [View {view_index}] كشف البوت! سيتم تخطي هذه المحاولة.")
            driver.save_screenshot(f"bot_detected_{view_index}.png")
            return

        # 4. محاكاة التمرير (Human Scroll)
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(random.uniform(1.5, 3))
        driver.execute_script("window.scrollTo(0, 0);")

        # 5. تشغيل الفيديو إجبارياً
        try:
            video = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
            # إلغاء الكتم والتشغيل برمجياً
            driver.execute_script("arguments[0].muted = false; arguments[0].play();", video)
            # محاولة النقر على زر التشغيل إذا وجد
            driver.execute_script("let btn = document.querySelector('.ytp-play-button'); if(btn) btn.click();")
        except:
            print("⚠️ لم يتم العثور على مشغل الفيديو، ربما الصفحة لم تحمل.")

        # 6. التقاط صورة إثبات (Proof) أن الفيديو يعمل
        time.sleep(5) # انتظار قليل بعد التشغيل
        screenshot_name = f"success_{view_index}.png"
        driver.save_screenshot(screenshot_name)
        print(f"📸 تم حفظ صورة للمشاهدة: {screenshot_name}")

        # 7. مدة المشاهدة
        watch_time = random.randint(45, 80)
        print(f"⏱️ [View {view_index}] جاري المشاهدة لمدة {watch_time} ثانية...")
        time.sleep(watch_time)

    except Exception as e:
        print(f"❌ خطأ غير متوقع في الجلسة {view_index}: {e}")
    finally:
        driver.quit()
        print(f"🏁 انتهاء الجلسة {view_index}")

def main():
    print(f"🔥 بدء البوت: الهدف {TOTAL_VIEWS} مشاهدة")
    # التأكد من وجود مجلد للصور إذا أردت تنظيمه (اختياري)
    
    # استخدام التكرار البسيط أو ThreadPool (لـ xvfb يفضل التتابع أو عدد قليل جداً)
    for i in range(TOTAL_VIEWS):
        run_session(i+1)
        # فاصل زمني مهم جداً لـ Tor
        sleep_time = random.randint(15, 30)
        print(f"💤 استراحة {sleep_time} ثانية...\n")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
