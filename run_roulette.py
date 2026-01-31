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
        # 1. 브라우저 실행
        browser = p.chromium.launch(headless=True)
        
        # 2. 컨텍스트 설정 (한국인 사용자로 완벽 위장)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()

        # 🕵️‍♂️ [슈퍼 스텔스 핵심] 브라우저 지문 세탁 스크립트
        # 이 스크립트는 G마켓 보안 프로그램이 '자동화 여부'를 확인할 때 거짓 정보를 줍니다.
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', {get: () => ['ko-KR', 'ko']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            const getParameter = WebGLRenderingContext.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Open Source Technology Center';
                if (parameter === 37446) return 'Mesa DRI Intel(R) HD Graphics 520 (Skylake GT2)';
                return getParameter(parameter);
            };
        """)

        try:
            # 1. 로그인 페이지 접속
            print("🌐 1. 로그인 페이지 접속")
            page.goto("https://signin.gmarket.co.kr/login/login")
            time.sleep(7)

            # 2. [순수 키 입력] 코랩 방식 유지
            print("⌨️ 2. 키 입력 시퀀스 시작 (슈퍼 스텔스 모드)")
            # 키보드 타입 시 delay를 주어 사람이 직접 치는 속도를 흉내냅니다.
            page.keyboard.type(USER_ID, delay=120) 
            time.sleep(1)
            page.keyboard.press("Tab")
            time.sleep(0.8)
            page.keyboard.press("Tab")
            time.sleep(1)
            page.keyboard.type(USER_PW, delay=130)
            time.sleep(2)

            # 📸 엔터 전 스크린샷 (입력 확인)
            page.screenshot(path="before_enter.png")
            send_tg("before_enter.png", "🔑 [슈퍼스텔스] 엔터 입력 직전")

            # 엔터 입력
            page.keyboard.press("Enter")
            print("⏳ 3. 로그인 처리 대기 (20초)")
            time.sleep(20)

            # 📸 로그인 시도 후 결과 스크린샷
            page.screenshot(path="after_login.png")
            send_tg("after_login.png", "✅ 로그인 시도 후 화면 (캡차 여부 확인)")

            # 3. 룰렛 페이지 이동 시도
            # URL에 'signin'이 남아있으면 로그인 실패(캡차 등)로 판단
            if "signin" not in page.url:
                print("📏 4. 룰렛 페이지 이동")
                page.goto("https://mobile.gmarket.co.kr/Pluszone")
                time.sleep(10)
                
                # 룰렛 좌표 클릭 (180, 626)
                print("🎯 5. 좌표 클릭")
                page.mouse.click(180, 626)
                time.sleep(5)

                # 최종 결과 촬영
                page.screenshot(path="final_result.png")
                send_tg("final_result.png", "🎉 슈퍼 스텔스 성공! 룰렛 완료")
            else:
                print("❌ 여전히 로그인 페이지입니다. (스텔스 실패)")

        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            page.screenshot(path="error_capture.png")
            send_tg("error_capture.png", f"🚨 에러 발생: {str(e)[:50]}")

        finally:
            browser.close()

if __name__ == "__main__":
    run()
