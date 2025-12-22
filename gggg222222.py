import time
import random
import threading
from stem import Signal
from stem.control import Controller
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- إعدادات تور ---
TOR_CONTROL_PORT = 9051
TOR_PASSWORD = "123456" 

# --- قائمة User-Agents متنوعة (ويندوز، أندرويد، لينكس، ماك) ---
USER_AGENTS = [
    # Windows - Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Android - Chrome Mobile
    "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    # Linux - Desktop
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # iPhone - Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    # macOS - Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
]

def change_tor_ip():
    """تغيير عنوان الـ IP لضمان هوية جديدة في كل محاولة"""
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            controller.authenticate(password=TOR_PASSWORD)
            controller.signal(Signal.NEWNYM)
        print("🔄 [IP] تم تبديل الهوية بنجاح..")
        time.sleep(8) 
    except Exception as e:
        print(f"⚠️ فشل تغيير IP: {e}")

def get_driver():
    """تشغيل المتصفح مع نظام تشغيل (User-Agent) عشوائي"""
    options = uc.ChromeOptions()
    
    # اختيار User-Agent عشوائي من القائمة
    selected_ua = random.choice(USER_AGENTS)
    options.add_argument(f'--user-agent={selected_ua}')
    
    options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
    options.add_argument("--mute-audio")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1280,720')

    try:
        # تشغيل المتصفح (استخدمنا subprocess لزيادة الثبات)
        driver = uc.Chrome(options=options, version_main=142, use_subprocess=True)
        print(f"📱 [System] الجهاز المحاكي: {selected_ua[:50]}...")
        return driver
    except Exception as e:
        print(f"❌ فشل فتح المتصفح: {e}")
        return None

def run_session(view_index):
    """تنفيذ جلسة المشاهدة مع تجاوز عقبات الصور المرفقة"""
    video_url = "https://youtube.com/shorts/MrKhyV4Gcog"
    change_tor_ip()
    
    driver = get_driver()
    if not driver: return

    try:
        wait = WebDriverWait(driver, 20)
        driver.get(video_url)
        time.sleep(6)

        # 1. تجاوز نافذة ملفات التعريف (الصورة 1)
        try:
            accept_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept') or contains(., 'agree') or contains(., 'وافق')]")))
            accept_btn.click()
            print(f"✅ [Session {view_index}] تم تخطي نافذة الموافقة.")
            time.sleep(2)
        except: pass

        # 2. فحص حماية "لست بوتاً" (الصورة 2)
        if "confirm you’re not a bot" in driver.page_source:
            print(f"❌ [Session {view_index}] كشف يوتيوب البوت! تغيير IP مطلوب.")
            return

        # 3. محاكاة حركة بشرية (Scroll)
        driver.execute_script("window.scrollTo(0, 400);")
        time.sleep(random.uniform(1, 3))
        driver.execute_script("window.scrollTo(0, 0);")

        # 4. تشغيل الفيديو (الصورة 3)
        try:
            video = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
            driver.execute_script("arguments[0].play();", video)
        except:
            print("⚠️ تنبيه: تعذر العثور على مشغل الفيديو.")

        watch_time = random.randint(40, 75)
        print(f"👀 [Session {view_index}] مشاهدة جارية لمدة {watch_time} ثانية...")
        time.sleep(watch_time)

    except Exception as e:
        print(f"❌ خطأ في الجلسة {view_index}: {e}")
    finally:
        driver.quit()
        print(f"🚪 إغلاق الجلسة {view_index}")

def main():
    total_views = 1000
    print(f"🚀 بدء التشغيل لاستهداف {total_views} مشاهدة بأنظمة تشغيل مختلفة...")
    
    for i in range(total_views):
        print(f"\n--- المحاولة {i+1} ---")
        run_session(i+1)
        # فاصل زمني عشوائي بين الجلسات لزيادة الأمان
        time.sleep(random.randint(10, 20))

if __name__ == "__main__":
    main()
