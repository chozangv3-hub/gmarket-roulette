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

def send_tg_photo(photo_path, caption):
    """사진 전송 함수"""
    if not os.path.exists(photo_path): return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}, files={'photo': photo}, timeout=20)
    except: pass

# --- 🕵️‍♂️ [핵심] 스텔스 브라우저 설정 ---
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument('--lang=ko_KR') # 1. 한국어 브라우저인 척 설정

# 2. 봇 탐지 회피를 위한 User-Agent 설정 (일반 윈도우 크롬처럼 보이게 함)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 3. 자동화 제어 메시지 제거 ('Chrome이 자동화된 테스트 소프트웨어에 의해 제어되고 있습니다' 숨김)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# 4. navigator.webdriver 플래그 숨김 (가장 중요: 이 값이 True면 바로 봇으로 걸림)
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 5. Navigator 속성 강제 변조 (자바스크립트로 한 번 더 흔적 지우기)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """
})

actions = ActionChains(driver)

try:
    print("🌐 1. 로그인 페이지 접속")
    driver.get("https://signin.gmarket.co.kr/login/login")
    time.sleep(5)
    
    # 2. 키 입력 시퀀스
    print("⌨️ 2. 키 입력 시퀀스 시작")
    
    # 입력 속도를 조금 더 사람처럼 불규칙하게 (너무 빠르면 기계로 의심)
    actions.send_keys(USER_ID).perform()
    time.sleep(0.8)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(0.8)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(0.8)
    actions.send_keys(USER_PW).perform()
    time.sleep(1.5) 
    
    # 엔터 전 스크린샷 (입력 확인용)
    driver.save_screenshot("before_enter.png")
    send_tg_photo("before_enter.png", "🔑 로그인 시도 직전 (ID/PW 입력)")

    actions.send_keys(Keys.ENTER).perform()
    
    print("⏳ 3. 로그인 대기 (20초)")
    time.sleep(20)
    
    # 경고창(Alert) 처리
    try:
        alert = driver.switch_to.alert
        print(f"⚠️ 경고창 발견: {alert.text}")
        alert.accept()
    except: pass
    
    driver.save_screenshot("after_login.png")
    send_tg_photo("after_login.png", "✅ 로그인 결과 화면")

    # --- 여기서부터 룰렛 로직 ---
    # (로그인이 성공했다면 메인 페이지나 룰렛 페이지로 이동했을 것임)
    if "signin" not in driver.current_url: # URL에 signin이 없으면 로그인 성공으로 간주
        print("룰렛 페이지 이동")
        driver.get("https://mobile.gmarket.co.kr/Pluszone")
        time.sleep(10)
        
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # 좌표 클릭
        target_body = driver.find_element(By.TAG_NAME, "html")
        actions.move_to_element_with_offset(target_body, 180, 626).click().perform()
        
        time.sleep(5)
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        driver.save_screenshot("final_result.png")
        send_tg_photo("final_result.png", f"🎉 {now} 룰렛 결과")
    else:
        print("여전히 로그인 페이지입니다 (CAPTCHA 의심)")

except Exception as e:
    print(f"❌ 에러 발생: {e}")
    driver.save_screenshot("error.png")
    send_tg_photo("error.png", f"🚨 에러 발생: {e}")

finally:
    driver.quit()
