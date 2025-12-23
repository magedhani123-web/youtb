import time
import random
import threading
from stem import Signal
from stem.control import Controller
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

# --- إعدادات السرعة ---
VIDEO_URL = "https://youtube.com/shorts/MrKhyV4Gcog"
TOTAL_VIEWS = 100
# ارفع هذا الرقم حسب قوة الخادم (3-5 هو المعدل الآمن لـ 2GB RAM)
MAX_WORKERS = 3 

TOR_CONTROL_PORT = 9051
TOR_PASSWORD = "123456"

# أقفال لتنظيم العمليات المشتركة
tor_lock = threading.Lock()
print_lock = threading.Lock()

# قائمة User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

def log(msg):
    """دالة طباعة منظمة لمنع تداخل النصوص"""
    with print_lock:
        print(msg)

def change_tor_ip():
    """تغيير IP بشكل سريع وآمن"""
    with tor_lock:
        try:
            with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
                controller.authenticate(password=TOR_PASSWORD)
                controller.signal(Signal.NEWNYM)
            # تقليل وقت انتظار التور إلى 5 ثواني (الحد الأدنى)
            time.sleep(5) 
        except Exception as e:
            log(f"⚠️ Tor Error: {e}")

def get_driver():
    """متصفح 'خفيف' وسريع (بدون صور)"""
    ua = random.choice(USER_AGENTS)
    options = uc.ChromeOptions()
    options.add_argument(f'--user-agent={ua}')
    options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
    options.add_argument("--mute-audio")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1024,768') # حجم أصغر قليلاً لتسريع الرندرة
    
    # 🔥 تسريع 1: منع تحميل الصور (يوفر الباندويدث والرام)
    options.add_argument('--blink-settings=imagesEnabled=false')
    
    # 🔥 تسريع 2: منع تحميل الإضافات غير الضرورية
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins-discovery")

    try:
        driver = uc.Chrome(options=options, use_subprocess=True, version_main=142)
        driver.set_page_load_timeout(45) # مهلة أقل لعدم تضييع الوقت
        return driver
    except Exception:
        return None

def run_session(view_index):
    change_tor_ip()
    driver = get_driver()
    if not driver: return

    try:
        wait = WebDriverWait(driver, 15)
        log(f"🚀 [View {view_index}] بدأ التحميل...")
        
        driver.get(VIDEO_URL)
        
        # 🔥 تسريع 3: التعامل السريع مع النوافذ
        try:
            # محاولة تخطي الكوكيز بسرعة فائقة (انتظار 3 ثواني فقط)
            btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept') or contains(., 'agree') or contains(., 'وافق')]"))
            )
            btn.click()
        except: pass

        if "bot" in driver.page_source:
            log(f"🚫 [View {view_index}] كشف بوت - تخطي")
            driver.quit()
            return

        # تشغيل الفيديو
        driver.execute_script("window.scrollTo(0, 200);")
        try:
            video = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
            driver.execute_script("arguments[0].muted = false; arguments[0].play();", video)
        except: pass

        # 🔥 تسريع 4: تقليل وقت المشاهدة للحد الأدنى المقبول (40-50 ثانية)
        watch_time = random.randint(40, 50)
        log(f"⏱️ [View {view_index}] مشاهدة {watch_time}ث...")
        time.sleep(watch_time)
        
        # حفظ إثبات (اختياري - يمكنك تعطيله لزيادة السرعة أكثر)
        # driver.save_screenshot(f"view_{view_index}.png")

    except Exception as e:
        log(f"❌ Error {view_index}: {str(e)[:50]}") # طباعة مختصرة للخطأ
    finally:
        try: driver.quit()
        except: pass

def main():
    log(f"🔥 بدء الوضع السريع: {MAX_WORKERS} متصفحات في نفس الوقت")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for i in range(TOTAL_VIEWS):
            futures.append(executor.submit(run_session, i+1))
            # تأخير بسيط جداً بين كل عملية وأخرى لمنع تجمد CPU
            time.sleep(3) 

        # انتظار انتهاء الجميع
        for future in futures:
            try: future.result()
            except: pass

if __name__ == "__main__":
    main()
