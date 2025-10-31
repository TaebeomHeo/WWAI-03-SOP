from playwright.sync_api import Playwright, sync_playwright, expect
from playwright.async_api import async_playwright
import asyncio

from smartThings_module.product_result import product
from smartThings_module.law_agree_result import law_agree

class AccountDataCollector:
    """
    삼성 SmartThings 웹페이지의 API 응답을 수집하고 처리하는 클래스
    
    - 웹페이지에서 발생하는 API 응답을 모니터링
    - 응답 데이터를 파싱하여 구조화된 데이터로 변환
    - 제품 정보, 동의 요건, 배너 정보 등을 수집
    """
    
    def __init__(self, page, context, target_urls, target_columns, banner_tag, banner_link_tag, consent_file_path):
        """
        AccountDataCollector 클래스 초기화
        
        Args:
            page: Playwright 페이지 객체
            context: Playwright 컨텍스트 객체
            target_urls: 모니터링할 API URL 딕셔너리 (main, product, meta, consent)
            target_columns: 수집할 데이터 컬럼 리스트
            banner_tag: 배너 텍스트를 추출할 CSS 선택자
            banner_link_tag: 배너 링크를 추출할 CSS 선택자
            consent_file_path: 동의 요건 파일 경로
        """
        self.page = page
        self.context = context
        self.target_urls = target_urls  # dict with keys: main, product, meta, consent
        self.target_columns = target_columns
        self.banner_tag = banner_tag
        self.banner_link_tag = banner_link_tag
        self.consent_file_path = consent_file_path

        self.main_headline_agree = "Hi {Name}, SmartThings selections for you"
        self.main_headline_disagree = "Hi {Name}, SmartThings makes life easier"

        self.main_description1_device = "Looks like you own {Device 1, Device 2} and are interested in {Scenario keyword 1, Scenario keyword 2}?"
        self.main_description1_no_device = "No devices yet? interested in {lifestyle1, lifestyle2}?"

        self.main_description2_agree  = "See what we’ve curated for you."
        self.main_description2_disagree = "Opt in to see personalized picks."




    async def setup_response_handler(self):
        """
        웹페이지의 모든 응답을 모니터링하는 핸들러를 설정하는 함수
        
        - 브라우저 컨텍스트에 응답 이벤트 리스너 등록
        - 타겟 URL과 일치하는 응답을 감지하면 해당 이벤트를 설정
        - 각 API 응답의 완료 상태를 추적
        """
        def handler(res):
            # 모든 응답에 대해 타겟 URL과 비교
            for key in self.target_urls:
                if res.url.startswith(self.target_urls[key]) and not self.called[key]:
                    self.called[key] = True  # 호출 완료 표시
                    self.responses[key] = res  # 응답 데이터 저장
                    getattr(self, f"{key}_event").set()  # 해당 이벤트 설정 (main_event, product_event 등)

        self.context.on("response", handler)  # 응답 이벤트 리스너 등록

    async def wait_for_responses(self, timeout=60):
        """
        모든 필요한 API 응답이 완료될 때까지 대기하는 함수
        
        Args:
            timeout: 대기 시간 (초, 기본값: 60초)
            
        - main, product, meta, consent 4개 API 응답을 모두 기다림
        - 모든 응답이 완료되거나 타임아웃이 발생하면 종료
        """
        await asyncio.wait_for(
            asyncio.gather(
                self.main_event.wait(),      # 메인 API 응답 대기
                self.product_event.wait(),   # 제품 API 응답 대기
                self.meta_event.wait(),      # 메타 API 응답 대기
                self.consent_event.wait(),   # 동의 API 응답 대기
                self.user_event.wait(),   # 유저 API 응답 대기
            ),
            timeout=timeout,
        )

    async def handle_authentication_popup(self):
        await self.page.wait_for_timeout(1000)
        await self.page.wait_for_selector("button.css-cmm9n1", timeout=10000)
        buttons = self.page.locator("button.css-cmm9n1")
        count = await buttons.count()
        for i in range(count):
            button = buttons.nth(i)
            if await button.is_visible():
                await button.click()

    async def process_responses(self, row):
        """
        수집된 API 응답들을 처리하여 구조화된 데이터로 변환하는 함수
        
        Args:
            row: 원본 행 데이터 (Account, country_code 등 포함)
            
        Returns:
            dict: 처리된 행 데이터 (모든 target_columns 포함)
            
        처리 과정:
        1. 메인 API 응답에서 추천 데이터 추출
        2. 메타 API와 제품 API에서 디바이스 정보 추출
        3. 동의 API에서 동의 요건 확인
        4. 동의가 필요한 경우 배너 정보 수집
        5. 모든 데이터를 하나의 딕셔너리로 통합
        """
        
        # 메인 API 응답 처리 - 추천 데이터 추출
        body_main = await self.responses["main"].json()
        json_data_main = body_main['resultData']['result']['recommend']  # 추천 데이터 부분 추출
       
        row_data = {col: json_data_main.get(col, "없음") for col in self.target_columns}  # 모든 타겟 컬럼에 대해 데이터 매핑
        
        # 메타 API 응답 처리 - 제품 메타데이터 추출
        body_meta = await self.responses["meta"].json()
        json_data_meta = body_meta['resultData']['result']

        # 제품 API 응답 처리 - 사용자 제품 목록 추출
        body_product = await self.responses["product"].json()
        json_data_product = body_product['resultData']['myProducts']['products']['productList']['items']

        body_user = await self.responses["user"].json()
        json_data_fullName= body_user['firstName']+ " "+ body_user['lastName']
        row_data['fullName'] = json_data_fullName  

        # 디바이스 정보 처리 - 메타데이터가 2개 이하면 첫 번째 제품을 중복 사용
        if len(json_data_meta) == 0:
            row['main_description1'] = self.main_description1_no_device

        elif len(json_data_meta) ==1:
            first_key = next(iter(json_data_meta))  # 첫 번째 키 추출
            first_value = json_data_meta[first_key]  # 첫 번째 값 추출
            Device1 = Device2 = first_value['nameCis']  # 같은 제품명을 두 디바이스에 할당
            row['main_description1'] = self.main_description1_device
            row_data['Device1'] = Device1  # 첫 번째 디바이스
            row_data['Device2'] = Device2  # 두 번째 디바이스
        else:
            # 제품 우선순위에 따라 상위 2개 제품 선택
            product_list = product(json_data_meta, json_data_product)
            Device1, Device2 = product_list.get_result()
            row['main_description1'] = self.main_description1_device
            row_data['Device1'] = Device1  # 첫 번째 디바이스
            row_data['Device2'] = Device2  # 두 번째 디바이스

        # 기본 정보 설정
        row_data['Account'] = row['Account']  # 계정 정보
        row_data['country_code'] = row['country_code']  # 국가 코드


        # 동의 API 응답 처리 - 상태 코드에 따라 다른 처리
        if self.responses["consent"].status == 204:  # 204: No Content (동의)
            law_agree_data = law_agree(self.consent_file_path, self.responses["consent"], str(row['country_code']))
            law_agree_result = law_agree_data.get_no_data_result()  # 동의 불필요 결과
           
        else:  # 200: OK (동의 필요)
            consent_json = await self.responses["consent"].json()
            law_agree_data = law_agree(self.consent_file_path, consent_json, str(row['country_code']))
            law_agree_result = law_agree_data.get_data_result()  # 동의 필요 결과

        # 동의가 필요한 경우 (X 표시) - 추가 데이터 수집
        if law_agree_result.iloc[0] == 'X':
            # 동의가 필요한 경우 N 버전의 스토리와 라이프스타일 데이터 사용
            for n in range(1, 4):  # storyIdRank1, 2, 3에 대해
                story_keyN = f"storyIdRank{n}N"  # N 버전 키 (예: storyIdRank1N)
                story_key = f"storyIdRank{n}"    # 일반 버전 키 (예: storyIdRank1)
                lifestyle_keyN = f"lifeStyleIdRank{n}N"  # N 버전 라이프스타일 키
                lifestyle_key = f"lifeStyleIdRank{n}"     # 일반 버전 라이프스타일 키
                row['main_headline'] = self.main_headline_disagree
                row['main_description2'] = self.main_description2_disagree

                # N 버전 데이터가 있으면 일반 버전에 할당
                if story_keyN in json_data_main:
                    row_data[story_key] = json_data_main[story_keyN]
                    row[story_key]  = json_data_main[story_keyN]
                    
                if lifestyle_keyN in json_data_main:
                    row_data[lifestyle_key] = json_data_main[lifestyle_keyN]
                    row[lifestyle_key]  = json_data_main[lifestyle_keyN]

            # 배너 정보 수집 - 동의가 필요한 경우에만 배너 표시
            banner_locator = self.page.locator(self.banner_tag)  # 배너 텍스트 요소
            banner_link_locator = self.page.locator(self.banner_link_tag)  # 배너 링크 요소
            
            # 배너가 존재하고 보이는 경우에만 정보 수집
            if await banner_locator.count() > 0 and await banner_locator.is_visible():
                row_data['banner_text'] = await banner_locator.inner_text()  # 배너 텍스트
                row_data['banner_link_text'] = await banner_link_locator.inner_text()  # 링크 텍스트
                row_data['banner_hyperlink'] = await banner_link_locator.get_attribute('href')  # 링크 URL
        else:
            row['main_headline'] = self.main_headline_agree
            row['main_description2'] = self.main_description2_agree

        return row_data  # 처리된 모든 데이터 반환
