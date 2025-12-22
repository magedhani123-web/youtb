import time
import random
from stem import Signal
from stem.control import Controller
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# إعدادات تور
TOR_CONTROL_PORT = 9051
TOR_PASSWORD = "123456" 

def change_tor_ip():
    """تغيير الهوية للحصول على IP جديد لضمان عدم كشف البوت"""
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            controller.authenticate(password=TOR_PASSWORD)
            controller.signal(Signal.NEWNYM)
        print("🔄 تم طلب IP جديد.. انتظار الاستقرار")
        time.sleep(8) 
    except Exception as e:
        print(f"⚠️ فشل تغيير IP: {e}")

def get_driver():
    """تشغيل متصفح بإعدادات تخفي لمحاكاة مستخدم حقيقي"""
    options = uc.ChromeOptions()
    options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
    options.add_argument("--mute-audio")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1280,720')
    
    try:
        # استخدام use_subprocess=True لزيادة استقرار المتصفح
        driver = uc.Chrome(options=options, version_main=142, use_subprocess=True)
        return driver
    except Exception as e:
        print(f"❌ فشل فتح المتصفح: {e}")
        return None

def run_session(url):
    """جلسة مشاهدة شاملة مع تجاوز العقبات الموضحة في الصور"""
    change_tor_ip()
    driver = get_driver()
    if not driver: return

    try:
        wait = WebDriverWait(driver, 20)
        driver.get(url)
        time.sleep(5)

        # 1. حل مشكلة نافذة ملفات التعريف (الصورة الأولى)
        try:
            # البحث عن زر "Accept all" بمختلف اللغات
            accept_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all') or contains(., 'I agree') or contains(., 'وافق')]")))
            accept_btn.click()
            print("✅ تم تجاوز نافذة ملفات التعريف")
            time.sleep(2)
        except:
            pass

        # 2. حل مشكلة "Sign in to confirm you're not a bot" (الصورة الثانية)
        if "confirm you’re not a bot" in driver.page_source:
            print("❌ تم كشف البوت! جاري إغلاق الجلسة وتغيير IP...")
            return

        # 3. محاكاة تفاعل بشري بسيط (Scroll) لزيادة الموثوقية
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(random.uniform(1, 3))
        driver.execute_script("window.scrollTo(0, 0);")

        # 4. تشغيل الفيديو والتأكد من عمله (الصورة الثالثة)
        try:
            video = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
            driver.execute_script("arguments[0].play();", video)
            # محاكاة الضغط على زر التشغيل إذا لم يعمل تلقائياً
            driver.execute_script("document.querySelector('.ytp-play-button')?.click();")
        except:
            print("⚠️ تعذر تشغيل الفيديو")

        watch_time = random.randint(45, 85)
        print(f"👀 مشاهدة ناجحة للمقطع لمدة {watch_time} ثانية")
        time.sleep(watch_time)

    except Exception as e:
        print(f"❌ خطأ أثناء الجلسة: {e}")
    finally:
        driver.quit()
        print("🚪 إغلاق المتصفح")

def main():
    video_url = "https://youtube.com/shorts/MrKhyV4Gcog"
    total_views = 100000
    for i in range(total_views):
        print(f"\n🔥 المحاولة {i+1} من {total_views}")
        run_session(video_url)
        time.sleep(random.randint(10, 20))

if __name__ == "__main__":
    main()
