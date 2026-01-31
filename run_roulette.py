import os
import time
import requests
import re
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

def get_free_proxies():
    """무료 프록시 리스트를 가져옵니다."""
    print("🔎 무료 프록시 리스트 수집 중...")
    try:
        # 여러 무료 프록시 API 중 하나 사용
        response = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
        proxies = response.text.split('\r\n')
        return [p for p in proxies if p]
    except:
        return []

def run_with_proxy(proxy):
    """특정 프록시를 사용하여 룰렛 실행"""
    with sync_playwright() as p:
        print(f"🚀 프록시 시도 중: {proxy}")
        try:
            # 프록시 설정 적용
            browser = p.chromium.launch(headless=True, proxy={"server": f"http://{proxy}"})
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="ko-KR"
            )
            page = context.new_page()
            
            # 접속 테스트 (타임아웃 30초)
            page.goto("https://signin.gmarket.co.kr/login/login", timeout=30000)
            time.sleep(5)

            # 키 입력 및 로그인
            page.keyboard.type(USER_ID, delay=100)
            page.keyboard.press("Tab")
            time.sleep(0.5)
            page.keyboard.press("Tab")
            time.sleep(0.5)
            page.keyboard.type(USER_PW, delay=100)
            
            page.screenshot(path="check_proxy.png")
            # 텔레그램으로 현재 프록시 접속 화면 전송 (확인용)
            send_tg("check_proxy.png", f"🌐 프록시({proxy}) 접속 확인")

            page.keyboard.press("Enter")
            time.sleep(15)

            # 캡차 여부 확인 및 룰렛 이동
            if "signin" not in page.url:
                print("✅ 로그인 성공! 룰렛 이동")
                page.goto("https://mobile.gmarket.co.kr/Pluszone")
                time.sleep(10)
                page.mouse.click(180, 626)
                time.sleep(5)
                page.screenshot(path="success.png")
                send_tg("success.png", "🎉 프록시 우회 성공 및 룰렛 완료!")
                browser.close()
                return True # 성공 시 True 반환
            else:
                print("❌ 여전히 캡차 발생 혹은 로그인 실패")
                browser.close()
                return False
        except Exception as e:
            print(f"⚠️ 프록시 연결 실패 혹은 타임아웃: {e}")
            return False

def main():
    proxies = get_free_proxies()
    # 상위 20개 프록시만 시도 (무료 프록시는 수백 개지만 대부분 죽어있음)
    for proxy in proxies[:20]:
        success = run_with_proxy(proxy)
        if success:
            break
        print("다음 프록시로 재시도합니다...")
        time.sleep(2)

if __name__ == "__main__":
    main()
