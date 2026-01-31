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

# --- [설정부] GitHub Secrets에서 환경 변수를 가져옵니다 ---
USER_ID = os.environ.get('GMARKET_ID')
USER_PW = os.environ.get('GMARKET_PW')
TELEGRAM_TOKEN = os.environ.get('TG_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TG_CHAT_ID')

def send_telegram_photo(photo_path, caption):
    """텔레그램으로 스크린샷과 메시지를 전송합니다."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            payload = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            files = {'photo': photo}
            response = requests.post(url, data=payload, files=files)
            return response.json()
    except Exception as e:
        print(f"텔레그램 전송 중 오류 발생: {e}")

# 브라우저 옵션 설정 (GitHub Actions 서버 환경 맞춤)
options = Options()
options.add_argument('--headless')  # 화면 없이 실행
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=400,800') # 로그인용 초기 사이즈
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

try:
    # 드라이버 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    actions = ActionChains(driver)

    # 1. G마켓 로그인
    print("🌐 G마켓 로그인 시도 중...")
    driver.get("https://signin.gmarket.co.kr/login/login")
    time.sleep(5)
    
    # Tab 키를 이용한 안정적인 로그인 방식
    actions.send_keys(USER_ID).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(USER_PW).send_keys(Keys.ENTER).perform()
    time.sleep(10)

    # 2. 창 확장 및 룰렛 페이지 이동
    print("📏 창 크기 확장(1920x2000) 및 룰렛 페이지 이동...")
    driver.set_window_size(1920, 2000)
    driver.get("https://mobile.gmarket.co.kr/Pluszone")
    time.sleep(15) # 페이지 요소 로딩 대기

    # 3. 정밀 좌표 타격 (사용자 검증 좌표: 180, 626)
    print("🎯 지정 좌표(180, 626) 조준 및 클릭...")
    driver.execute_script("window.scrollTo(0, 0);") # 스크롤 최상단 고정
    time.sleep(2)
    
    # 자바스크립트 클릭 + 물리 마우스 클릭 혼합 (확실한 트리거)
    driver.execute_script("document.elementFromPoint(180, 626).click();")
    target_body = driver.find_element(By.TAG_NAME, "html")
    actions.move_to_element_with_offset(target_body, 180, 626).click().perform()
    
    # 4. 결과 대기 및 스크린샷 저장
    print("📸 3초 대기 후 결과 촬영 중...")
    time.sleep(3)
    
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name = f"Gmarket_{now}.png"
    file_path = os.path.join(os.getcwd(), file_name)
    
    driver.save_screenshot(file_path)
    print(f"✅ 스크린샷 저장 완료: {file_name}")

    # 5. 텔레그램 전송
    print("📤 텔레그램으로 결과 전송 중...")
    send_telegram_photo(file_path, f"[{now}] G마켓 룰렛 자동 응모 결과입니다.")
    print("🚀 모든 작업이 완료되었습니다!")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
finally:
    if 'driver' in locals():
        driver.quit()
