import time
import random
import os
import shutil
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- إعدادات آمنة جداً ---
VIDEO_URL = "https://youtube.com/shorts/MrKhyV4Gcog"
TOR_PROXY = "socks5://127.0.0.1:9050"

def get_driver():
    options = uc.ChromeOptions()
    # عزل تام في مجلد عشوائي
    random_id = random.randint(1000, 9999)
    profile_dir = os.path.abspath(f"temp_profile_{random_id}")
    
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument(f'--proxy-server={TOR_PROXY}')
    options.add_argument("--mute-audio")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu') # تعطيل الجرافيك لتوفير الرام
    
    try:
        # استخدام driver_executable_path بشكل تلقائي
        driver = uc.Chrome(options=options, use_subprocess=False) # جرب False هنا للاستقرار
        driver.set_page_load_timeout(100)
        return driver, profile_dir
    except Exception as e:
        print(f"❌ فشل فتح المتصفح: {e}")
        return None, None

def run_single_view(count):
    print(f"\n🔥 بدأت المحاولة رقم {count}")
    driver, p_dir = get_driver()
    if not driver: return

    try:
        print(f"🚀 [View {count}] جاري تحميل اليوتيوب...")
        driver.get(VIDEO_URL)
        
        # انتظار طويل لضمان التحميل عبر تور البطيء
        time.sleep(10)
        
        # محاولة الضغط على أي زر موافقة
        try:
            btns = driver.find_elements(By.TAG_NAME, "button")
            for b in btns:
                if "Accept" in b.text or "agree" in b.text or "وافق" in b.text:
                    b.click()
                    break
        except: pass

        # تشغيل الفيديو
        driver.execute_script("document.querySelectorAll('video').forEach(v => v.play())")
        
        watch_time = random.randint(45, 60)
        print(f"✅ تعمل الآن.. مشاهدة لـ {watch_time} ثانية")
        time.sleep(watch_time)

    except Exception as e:
        print(f"❌ خطأ أثناء التشغيل: {e}")
    finally:
        driver.quit()
        if p_dir: shutil.rmtree(p_dir, ignore_errors=True)
        print(f"🏁 انتهت المحاولة {count}")

if __name__ == "__main__":
    # تشغيل متتابع (واحد تلو الآخر) لضمان عدم حدوث RemoteDisconnected
    for i in range(100):
        run_single_view(i + 1)
        # تغيير الـ IP يدوياً هنا إذا كنت تملك كود تغيير IP تور
        time.sleep(5)
