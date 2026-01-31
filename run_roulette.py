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

# --- [설정부] ---
USER_ID = os.environ.get('GMARKET_ID')
USER_PW = os.environ.get('GMARKET_PW')
TELEGRAM_TOKEN = os.environ.get('TG_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TG_CHAT_ID')

def send_tg(photo_path, caption):
    """텔레그램 전송 함수"""
    if not os.path.exists(photo_path):
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}, files={'photo': photo}, timeout=20)
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,2000')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
actions = ActionChains(driver)

def capture_and_send(step_name, caption):
    """경고창 처리 후 사진 촬영 및 전송"""
    try:
        alert = driver.switch_to.alert
        print(f"⚠️ 경고창 발견: {alert.text}")
        alert.accept()
        time.sleep(1)
    except:
        pass
    
    filename = f"{step_name}.png"
    driver.save_screenshot(filename)
    send_tg(filename, caption)

try:
    # 1. 로그인 페이지 접속
    print("🌐 1. 로그인 페이지 접속")
    driver.get("https://signin.gmarket.co.kr/login/login")
    time.sleep(10)

    # 2. [코랩 방식] 순수 키 입력 시퀀스
    print("⌨️ 2. 키 입력 시퀀스 시작")
    actions.send_keys(USER_ID).perform()
    time.sleep(1)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(1)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(1)
    actions.send_keys(USER_PW).perform()
    time.sleep(2) # 입력 완료 후 잠시 대기
    
    # 📸 [추가] 비밀번호 입력 후 엔터 치기 직전 촬영
    print("📸 2.5 비밀번호 입력 확인샷 촬영")
    capture_and_send("STEP_BEFORE_ENTER", "🔑 엔터 키 입력 직전 화면 (ID/PW 입력 확인)")
    
    # 엔터 입력
    actions.send_keys(Keys.ENTER).perform()
    
    print("⏳ 3. 로그인 처리 대기 (25초)")
    time.sleep(25)
    capture_and_send("STEP_AFTER_LOGIN", "✅ 로그인 시도 후 결과 화면")

    # 3. 룰렛 페이지 이동
    print("📏 4. 룰렛 페이지 이동")
    driver.get("https://mobile.gmarket.co.kr/Pluszone")
    time.sleep(15)
    capture_and_send("STEP_ROULETTE_PAGE", "🎡 룰렛 페이지 접속 완료")

    # 4. 좌표 타격 (180, 626)
    print("🎯 5. 좌표 타격")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(3)
    driver.execute_script("document.elementFromPoint(180, 626).click();")
    
    html_tag = driver.find_element(By.TAG_NAME, "html")
    actions.move_to_element_with_offset(html_tag, 180, 626).click().perform()
    
    print("📸 6. 최종 결과 대기")
    time.sleep(10)
    capture_and_send("STEP_FINAL_RESULT", "🎉 최종 룰렛 결과")

except Exception as e:
    print(f"❌ 에러 발생: {e}")
    # 📸 [추가] 에러 발생 시 즉시 촬영하여 전송
    capture_and_send("STEP_ERROR_OCCURRED", f"🚨 에러 발생 화면\n메시지: {str(e)[:50]}")

finally:
    driver.quit()
