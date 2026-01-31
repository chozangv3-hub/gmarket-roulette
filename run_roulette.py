import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# --- [설정부] ---
USER_ID = os.environ.get('GMARKET_ID')
USER_PW = os.environ.get('GMARKET_PW')
TELEGRAM_TOKEN = os.environ.get('TG_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TG_CHAT_ID')

def test_telegram_connection():
    """시작하자마자 텔레그램 연결부터 확인하는 함수"""
    print(f"📡 텔레그램 연결 테스트 시작...")
    print(f"Token 확인(일부): {TELEGRAM_TOKEN[:5]}..." if TELEGRAM_TOKEN else "❌ Token 없음")
    print(f"Chat ID 확인: {TELEGRAM_CHAT_ID}" if TELEGRAM_CHAT_ID else "❌ ID 없음")

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': "🚀 [테스트] GitHub Actions에서 보낸 첫 메시지입니다! (설정 성공)"}
    
    try:
        resp = requests.post(url, data=payload, timeout=10)
        print(f"전송 결과 코드: {resp.status_code}")
        print(f"응답 내용: {resp.text}")
        if resp.status_code == 200:
            print("✅ 텔레그램 메시지 전송 성공!")
        else:
            print("❌ 텔레그램 전송 실패. 토큰/ID를 확인하세요.")
    except Exception as e:
        print(f"❌ 연결 에러 발생: {e}")

def send_tg_photo(photo_path, caption):
    """사진 전송 함수"""
    if not os.path.exists(photo_path): return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}, files={'photo': photo}, timeout=20)
    except: pass

# --- 메인 로직 시작 ---

# 1. [가장 중요] 텔레그램부터 테스트
test_telegram_connection()

# ... (이하 브라우저 설정 및 로직) ...
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,2000')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
actions = ActionChains(driver)

try:
    print("🌐 1. 로그인 페이지 접속")
    driver.get("https://signin.gmarket.co.kr/login/login")
    time.sleep(5)
    
    # 2. 아이디/비밀번호 입력
    print("⌨️ 2. 키 입력 시퀀스 시작")
    actions.send_keys(USER_ID).perform()
    time.sleep(0.5)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(0.5)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(0.5)
    actions.send_keys(USER_PW).perform()
    time.sleep(1)
    
    # 비밀번호 입력 직후 (엔터 전) 스크린샷
    print("📸 엔터 전 스크린샷 촬영")
    driver.save_screenshot("before_enter.png")
    send_tg_photo("before_enter.png", "🔑 엔터 키 입력 전 화면")

    actions.send_keys(Keys.ENTER).perform()
    
    print("⏳ 3. 로그인 대기 (20초)")
    time.sleep(20)
    
    # 로그인 직후 경고창 처리 및 스크린샷
    try:
        alert = driver.switch_to.alert
        print(f"⚠️ 경고창 발견: {alert.text}")
        alert.accept()
    except: pass
    
    driver.save_screenshot("after_login.png")
    send_tg_photo("after_login.png", "✅ 로그인 시도 후 화면")

except Exception as e:
    print(f"❌ 에러 발생: {e}")
    driver.save_screenshot("error.png")
    send_tg_photo("error.png", f"🚨 에러 발생: {e}")

finally:
    driver.quit()
