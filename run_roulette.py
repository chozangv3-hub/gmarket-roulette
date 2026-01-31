import os
import time
import asyncio
from playwright.sync_api import sync_playwright

# --- [설정부] ---
USER_ID = os.environ.get('GMARKET_ID')
USER_PW = os.environ.get('GMARKET_PW')
# ... 텔레그램 설정 동일 ...

def run():
    with sync_playwright() as p:
        # 브라우저 실행 (한국 로케일 설정)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            geolocation={"longitude": 126.9779, "latitude": 37.5665}, # 서울 좌표
            permissions=["geolocation"]
        )
        
        page = context.new_page()
        
        # 1. 로그인 페이지 이동
        page.goto("https://signin.gmarket.co.kr/login/login")
        time.sleep(5)
        
        # 2. [코랩 방식] 순수 키 입력
        page.keyboard.type(USER_ID)
        time.sleep(1)
        page.keyboard.press("Tab")
        time.sleep(1)
        page.keyboard.press("Tab")
        time.sleep(1)
        page.keyboard.type(USER_PW)
        time.sleep(1)
        
        # 엔터 전 스샷
        page.screenshot(path="before_enter.png")
        # 텔레그램 전송 함수 호출...
        
        page.keyboard.press("Enter")
        time.sleep(15)
        
        # 3. 룰렛 이동 및 좌표 클릭
        page.goto("https://mobile.gmarket.co.kr/Pluszone")
        time.sleep(10)
        
        # 좌표 클릭 (Playwright는 좌표 클릭이 매우 정확합니다)
        page.mouse.click(180, 626)
        
        time.sleep(5)
        page.screenshot(path="final.png")
        # 텔레그램 전송...
        
        browser.close()

if __name__ == "__main__":
    run()
