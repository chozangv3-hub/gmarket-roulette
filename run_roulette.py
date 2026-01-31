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

def send_tg(photo_path, caption):
    """텔레그램 전송 함수"""
    if not os.path.exists(photo_path): return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}, files={'photo': photo}, timeout=15)
    except: pass

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,2000')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
actions = ActionChains(driver)

try:
    # 1. 로그인 페이지 접속
    print("🌐 1. 로그인 페이지 접속")
    driver.get("https://signin.gmarket.co.kr/login/login")
    time.sleep(10) # 페이지가 완전히 로딩될 때까지 충분히 대기
    driver.save_screenshot("step1_login_page.png")
    send_tg("step1_login_page.png", "1. 로그인 페이지 접속 완료 (입력 시작 전)")

    # 2. 코랩 방식: 요소 찾기 없이 즉시 키 입력 시작
    print("⌨️ 2. 순수 키 입력 시퀀스 시작 (Tab-Tab 방식)")
    # 아이디 입력 -> Tab -> Tab -> 비밀번호 입력 -> Enter
    actions.send_keys(USER_ID).perform()
    time.sleep(1)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(1)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(1)
    actions.send_keys(USER_PW).perform()
    time.sleep(1)
    actions.send_keys(Keys.ENTER).perform()
    
    print("⏳ 3. 로그인 처리 및 세션 대기 (25초)")
    time.sleep(25) # 로그인 후 메인 이동 및 세션 유지를 위해 충분히 대기
    driver.save_screenshot("step2_after_login.png")
    send_tg("step2_after_login.png", "2. 로그인 시도 후 결과 화면")

    # 3. 룰렛 페이지 이동
    print("📏 4. 룰렛 페이지 이동")
    driver.get("https://mobile.gmarket.co.kr/Pluszone")
    time.sleep(15)
    driver.save_screenshot("step3_roulette_page.png")
    send_tg("step3_roulette_page.png", "3. 룰렛 페이지 도착 화면")

    # 4. 검증된 좌표 타격 (180, 626)
    print("🎯 5. 좌표 타격 실행")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(3)
    
    # 자바스크립트 클릭 시도
    driver.execute_script("document.elementFromPoint(180, 626).click();")
    # 물리 마우스 클릭 시도
    target_body = driver.find_element(By.TAG_NAME, "html")
    actions.move_to_element_with_offset(target_body, 180, 626).click().perform()
    
    print("📸 6. 최종 결과 대기 및 촬영")
    time.sleep(5)
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    final_file = f"Final_{now}.png"
    driver.save_screenshot(final_file)
    send_tg(final_file, f"✅ {now} G마켓 룰렛 결과")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    # 경고창(Alert) 발생 시 처리 로직
    alert_msg = "없음"
    try:
        alert = driver.switch_to.alert
        alert_msg = alert.text
        alert.accept()
    except: pass
    
    error_file = "error_capture.png"
    driver.save_screenshot(error_file)
    send_tg(error_file, f"🚨 에러 발생!\n알림내용: {alert_msg}\n상세에러: {str(e)[:50]}")

finally:
    driver.quit()
