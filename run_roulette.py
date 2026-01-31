import os
import time
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- [설정부] GitHub Secrets ---
USER_ID = os.environ.get('GMARKET_ID')
USER_PW = os.environ.get('GMARKET_PW')
TELEGRAM_TOKEN = os.environ.get('TG_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TG_CHAT_ID')

def send_telegram_photo(photo_path, caption):
    """텔레그램으로 사진 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            payload = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            files = {'photo': photo}
            requests.post(url, data=payload, files=files)
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
actions = ActionChains(driver)

try:
    # 1. 로그인 단계 (이전 성공 방식: Tab 입력)
    print("🌐 G마켓 로그인 시도 중 (Tab 입력 방식)...")
    driver.get("https://signin.gmarket.co.kr/login/login")
    time.sleep(7) # 페이지 안정화 대기
    
    # 순차적 키 입력 (안정성을 위해 중간중간 1초 대기)
    actions.send_keys(USER_ID).perform()
    time.sleep(1)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(1)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(1)
    actions.send_keys(USER_PW).perform()
    time.sleep(1)
    actions.send_keys(Keys.ENTER).perform()
    
    print("⏳ 로그인 처리 대기 중 (15초)...")
    time.sleep(15)

    # 2. 룰렛 페이지 이동
    print("📏 룰렛 페이지 이동...")
    driver.set_window_size(1920, 2000)
    driver.get("https://mobile.gmarket.co.kr/Pluszone")
    time.sleep(15)

    # 3. 좌표 타격 (180, 626)
    print("🎯 지정 좌표(180, 626) 클릭...")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(3)
    
    # 자바스크립트 클릭 + 물리 마우스 클릭
    driver.execute_script("document.elementFromPoint(180, 626).click();")
    target_body = driver.find_element(By.TAG_NAME, "html")
    actions.move_to_element_with_offset(target_body, 180, 626).click().perform()
    
    # 4. 결과 저장 및 전송
    time.sleep(5)
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    file_path = f"Gmarket_{now}.png"
    driver.save_screenshot(file_path)
    send_telegram_photo(file_path, f"✅ [{now}] G마켓 룰렛 완료!")

except Exception as e:
    # 🚨 에러 발생 시 처리 (스크린샷 전송)
    print(f"❌ 오류 발생: {e}")
    error_now = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    error_file = f"ERROR_{error_now}.png"
    
    try:
        # 팝업창이 떠있으면 닫기 시도
        alert = driver.switch_to.alert
        alert.accept()
    except:
        pass
        
    driver.save_screenshot(error_file)
    send_telegram_photo(error_file, f"🚨 오류 발생!\n내용: {str(e)[:100]}")

finally:
    driver.quit()
