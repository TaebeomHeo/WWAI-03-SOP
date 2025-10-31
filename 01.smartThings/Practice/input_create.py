import re
from playwright.sync_api import Playwright, sync_playwright, expect
from playwright.async_api import async_playwright
import pandas as pd

import asyncio

async def smartThings_main(playwright: Playwright) -> None:


    # Chrome 브라우저 설정
    CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    browser = await playwright.chromium.launch(
        headless=False,  # 브라우저 창 표시
        executable_path=CHROME_PATH,  # Chrome 실행 파일 경로
        args=[
        #"--user-agent=D2CEST-AUTO-70a4cf16 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36.D2CEST-AUTO-70a4cf16",  # 사용자 에이전트 설정
        #"--incognito",  # 시크릿 모드
        "--start-maximized",  # 최대화된 창으로 시작
        #"--remote-allow-origins=*"  # 원격 연결 허용
        ]
    )

    context1 = await browser.new_context()
    
    page1 = await context1.new_page()
    


    #await page1.goto(""https://webmail.wisewires.com")
    await page1.goto("https://naver.com")

    await page1.wait_for_timeout(2000)



    context2 = await browser.new_context()
    page2 = await context2.new_page()

    await page2.goto("https://webmail.wisewires.com/")
    await page2.wait_for_timeout(3000)

    text = await page2.locator("a[href='#tabUser']").inner_text()
    print(text)  # 출력: "사용자 모드"


    await page1.wait_for_timeout(1000)
    await page1.locator("input[name='query']").fill(text)
    await page1.wait_for_timeout(4000)
    #await page2.locator("input[type='text']").fill("test")  

    #await page2.locator("input[name='mail']").fill("test")
    
    
    #await page2.get_by_role("textbox", name="mail").fill("test")
    await page2.wait_for_timeout(3000)

    await page1.close()
    await context1.close()
    await page2.close()
    await context2.close()
  
    await browser.close()



async def main():
    """
    메인 함수 - Playwright 실행 및 run 함수 호출
    """
    async with async_playwright() as playwright:
        await smartThings_main(playwright)  # run 함수 실행
        
asyncio.run(main())  # 비동기 실행