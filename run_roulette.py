import os
import time
import requests
from playwright.sync_api import sync_playwright

# --- [설정부] ---
USER_ID = os.environ.get('GMARKET_ID')
USER_PW = os.environ.get('GMARKET_PW')
TELEGRAM_TOKEN = os.environ.get('TG_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TG_CHAT_ID')

def send_tg(photo_path, caption):
    if not os.path.exists(photo_path): return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}, files={'photo': photo}, timeout=20)
    except: pass

def run():
    with sync_playwright() as p:
        # 한국인 브라우저처럼 위장하여 접속
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            viewport={'width': 1920, 'height': 2000}
        )
        page = context.new_page()

        try:
            # 1. 로그인 페이지 접속
            print("🌐 1. 로그인 페이지 접속")
            page.goto("https://signin.gmarket.co.kr/login/login")
            time.sleep(7)

            # 2. [순수 키 입력] ID -> Tab -> Tab -> PW
            print("⌨️ 2. 키 입력 시퀀스 시작")
            page.keyboard.type(USER_ID, delay=100) # 사람처럼 보이게 딜레이 추가
            time.sleep(1)
            page.keyboard.press("Tab")
            time.sleep(0.5)
            page.keyboard.press("Tab")
            time.sleep(1)
            page.keyboard.type(USER_PW, delay=100)
            time.sleep(2)

            # 📸 엔터 전 스크린샷
            page.screenshot(path="before_enter.png")
            send_tg("before_enter.png", "🔑 엔터 입력 직전 화면")

            # 엔터 입력
            page.keyboard.press("Enter")
            print("⏳ 3. 로그인 처리 대기 (20초)")
            time.sleep(20)

            # 📸 로그인 후 결과 스크린샷
            page.screenshot(path="after_login.png")
            send_tg("after_login.png", "✅ 로그인 시도 후 결과")

            # 3. 룰렛 페이지 이동
            print("📏 4. 룰렛 페이지 이동")
            page.goto("https://mobile.gmarket.co.kr/Pluszone")
            time.sleep(10)
            
            # 📸 룰렛 페이지 도착 확인
            page.screenshot(path="roulette_page.png")
            send_tg("roulette_page.png", "🎡 룰렛 페이지 도착")

            # 4. 좌표 타격 (180, 626)
            print("🎯 5. 좌표 클릭")
            page.mouse.click(180, 626)
            time.sleep(5)

            # 📸 최종 결과 촬영
            page.screenshot(path="final_result.png")
            send_tg("final_result.png", "🎉 최종 룰렛 결과")

        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            page.screenshot(path="error_capture.png")
            send_tg("error_capture.png", f"🚨 에러 발생: {str(e)[:50]}")

        finally:
            browser.close()

if __name__ == "__main__":
    run()
