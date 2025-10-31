import re
from playwright.sync_api import Playwright, sync_playwright, expect
from playwright.async_api import async_playwright
import pandas as pd
#from lxml import html
import asyncio
#import time
import datetime
import os
import sys
import requests
from requests.exceptions import HTTPError

# 모듈 폴더를 Python 경로에 추가 (상위 디렉토리의 smartThings_module)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # Practice 폴더의 상위 디렉토리

# sys.path에 모듈 폴더 추가 (없을 경우만)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
    print(f"Added module path: {parent_dir}")

from smartThings_module.rowdata_excel import RowDataExcel
from smartThings_module.html_result import htmlExtractor
from smartThings_module.response_handler import AccountDataCollector
from smartThings_module.compare_result import CompareProcess

#print 적용 시 전체 컬럼이 모두 나오게 하는 코드
pd.set_option('display.max_columns', None)

##############################################데이터 수집 대상 컬럼 정의##############################################
# 데이터 수집 대상 컬럼 정의
target_columns = [    
        'Account',    # 계정 정보
        'main_headline', 'main_description', 'main_description1', 'main_description2',  # 메인 정보
        'storyIdRank1', 'storyIdRank2', 'storyIdRank3',  # 스토리 ID들
        'storyIdRank1_title', 'storyIdRank1_desc',  # 스토리 1 제목/설명
        'storyIdRank1_rec1','storyIdRank1_rec2','storyIdRank1_rec3','storyIdRank1_rec4','storyIdRank1_rec5',  # 스토리 1 추천 제품들
        'storyIdRank2_title', 'storyIdRank2_desc',  # 스토리 2 제목/설명
        'storyIdRank2_rec1','storyIdRank2_rec2','storyIdRank2_rec3','storyIdRank2_rec4','storyIdRank2_rec5',  # 스토리 2 추천 제품들
        'storyIdRank3_title', 'storyIdRank3_desc',  # 스토리 3 제목/설명
        'storyIdRank3_rec1','storyIdRank3_rec2','storyIdRank3_rec3','storyIdRank3_rec4','storyIdRank3_rec5',  # 스토리 3 추천 제품들
        'lifeStyleIdRank1','lifeStyleIdRank2','Scenariokeyword1','Scenariokeyword2',  # 라이프스타일 및 시나리오 키워드
        'country_code','Device1','Device2','banner_text', 'banner_link_text','banner_hyperlink'  # 국가, 디바이스, 배너 정보
        ]
main_result = pd.DataFrame(columns=target_columns)  # 최종 결과를 저장할 DataFrame
target_columns = main_result.columns

##########################################엑셀 파일 경로 설정########################################################
samsung_project_path = r'C:\Users\WW\Desktop\삼성 프로젝트 관련 파일' # 삼성 프로젝트 관련 파일 경로

now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')  # 현재 시간을 파일명에 포함
result_full_path = samsung_project_path+r'\result_'+now  # 결과 저장 디렉토리
result_file_path = result_full_path+r'\테스트결과_result.xlsx'  # 최종 결과 파일 경로

format_data_path = samsung_project_path + r'\Test data matrix (Umbrella merge).xlsx'  # 메인 테스트 데이터 파일
contents_data_path = samsung_project_path + r'\contents'  # 콘텐츠 매핑 파일 디렉토리
umbrella_file_path = samsung_project_path+r'\umbrella'  # 우산 파일 디렉토리

consent_file_path = samsung_project_path + r'\국가별 마케팅 동의 요건.xlsx'  # 동의 요건 파일
compare_item_path = samsung_project_path + r'\계정별비교항목.xlsx'  # 비교 항목 파일

# 메인 테스트 데이터 Excel 파일 설정
usecols = 'C,U,V,X,Y,Z'  # 사용할 Excel 컬럼
tc_sheet_name = "Test data matrix"  # Excel 시트명

# 파일 경로 설정
os.mkdir(result_full_path)  # 결과 디렉토리 생성

#################################### 대상 국가 코드 설정############################################################

country_codes = ['DE']

#################################### 기본 배너 텍스트 설정############################################################
format_banner_text = 'General recommendations are shown by default. Opt in to required settings on the Privacy tab of your Samsung Account for a more personalized experience.'
format_banner_link_text = 'Go to Samung Account'
format_banner_hyperlink = 'http://account.samsung.com/'

banner_tag = 'p.myd26-my-story-st__marketing-description'  # 배너 텍스트 선택자
banner_link_tag = 'a.cta.cta--underline.cta--black'  # 배너 링크 선택자

#################################### HTML 요소 선택자 설정############################################################
main_headline_tag = 'h2[class="myd26-my-story-st__wrapper-headline"]'  # 메인 헤드라인 선택자
main_desc_tag = 'p[class="myd26-my-story-st__wrapper-description"]'  # 메인 설명 선택자
story_data_tag = 'div[class="myd26-my-story-st"]'  # 스토리 데이터 선택자

############################################### Excel 데이터 처리 객체 생성 및 초기화##################################


rowdata_excel = RowDataExcel(format_data_path,contents_data_path,umbrella_file_path,country_codes,tc_sheet_name ,usecols,
                             format_banner_text,format_banner_link_text,format_banner_hyperlink)
rowdata_excel.load_excel()  # Excel 파일 로드
rowdata_excel.process_rows(2)  # 행 데이터 처리 (2행까지)
rowdata_excel.copy_format_data()  # 국가별 데이터 복사

format_result = rowdata_excel.get_result()  # 포맷 결과 가져오기
format_result.to_excel(r'C:\Users\WW\Desktop\테스트_결과_format.xlsx', index=False, sheet_name='테스트결과')  # 포맷 결과 저장















async def smartThings_main(playwright: Playwright) -> None:
    """
    메인 실행 함수 - 각 계정별로 웹 자동화 및 데이터 수집을 수행
    
    - Playwright를 사용하여 브라우저 자동화
    - 각 계정별로 로그인 및 데이터 수집
    - API 응답 모니터링 및 HTML 데이터 추출
    - 스크린샷 캡처 및 결과 저장
    """

    for idx, row in format_result.iterrows():  # 각 계정별로 반복 처리
        
        # 같은 row에 대해 최대 3회 재시도
        for attempt in range(1, 4):
            page = None
            context = None
            browser = None
            try:
                browser = await playwright.chromium.launch(
                    headless=False,  # 브라우저 창 표시
                    args=[
                    "--user-agent=D2CEST-AUTO-70a4cf16 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36.D2CEST-AUTO-70a4cf16",  # 사용자 에이전트 설정
                    #"--incognito",  # 시크릿 모드
                    #"--start-maximized",  # 최대화된 창으로 시작
                    #"--remote-allow-origins=*"  # 원격 연결 허용
                    ]
                )

                # API 엔드포인트 URL 설정
                target_url_main = f"https://hshopfront.samsung.com/aemapi/v6/mysamsung/{row['country_code'].lower()}/scv/user/recommend/st/story"  # 메인 스토리 API
                target_url_meta = f"https://hshopfront.samsung.com/aemapi/v6/mysamsung/{row['country_code'].lower()}/scv/product/meta"  # 제품 메타데이터 API
                target_url_product = f"https://hshopfront.samsung.com/aemapi/v6/mysamsung/{row['country_code'].lower()}/scv/newproducts"  # 새 제품 API
                target_url_consent = f"https://account.samsung.com/api/v1/consent/required"  # 동의 요건 API

                # 모든 API URL을 딕셔너리로 구성
                taget_url_total = {"main" : target_url_main,
                             "meta" : target_url_meta,
                             "product" : target_url_product,
                             "consent" : target_url_consent
                             }
                
                context = await browser.new_context()  # 새 브라우저 컨텍스트 생성
                
                page = await context.new_page()  # 새 페이지 생성

                # SmartThings 페이지로 이동
                response= await page.goto(f"https://hshopfront.samsung.com/{row['country_code'].lower()}/mypage/mysmartthings")
                
                # 응답 상태 확인 - 로그인 과정 전에 먼저 확인
                if response:
                    if response.status == 200:
                        print("200 ok")    # 성공

                        #################################################1첫번째로 주석 풀어야함#######################
                        # 로그인 과정 실행
                        await page.get_by_role("textbox", name="사용자 이름").click()  # 사용자명 입력 필드 클릭
                        await page.wait_for_timeout(1000)  # 1초 대기
                        await page.get_by_role("textbox", name="사용자 이름").fill("qauser")  # 사용자명 입력
                        await page.wait_for_timeout(1000)  # 1초 대기
                        await page.get_by_role("textbox", name="암호").click()  # 비밀번호 입력 필드 클릭
                        await page.wait_for_timeout(1000)  # 1초 대기
                        await page.get_by_role("textbox", name="암호").fill("qauser1!")  # 비밀번호 입력
                        await page.wait_for_timeout(1000)  # 1초 대기
                        await page.get_by_role("button", name="로그인").click()  # 로그인 버튼 클릭
                        await page.wait_for_timeout(5000)  # 1초 대기
                        
                        ###########################2번째로 주석 풀어야함############################################3
                        # 계정 정보 입력
                        await page.locator("input[name='account']").click()  # 계정 입력 필드 클릭
                        await page.wait_for_timeout(1000)  # 1초 대기
                        await page.locator("input[name='account']").fill(format_result['Account'].values[idx])  # 계정 정보 입력
                        await page.wait_for_timeout(1000)  # 1초 대기
                        await page.locator("button[type='button']").nth(0).click()  # 첫 번째 버튼 클릭
                        await page.wait_for_timeout(1000)  # 1초 대기
                        await page.locator("input[type='password']").fill('mypage1!')  # 비밀번호 입력
                        await page.wait_for_timeout(1000)  # 1초 대기
                        await page.locator("button[type='button']").nth(2).click()  # 세 번째 버튼 클릭 (로그인)
                        
                    elif response.status == 400:
                        # 400 에러 시 로그인 과정 스킵하고 다음 시도로 넘어감
                        raise RuntimeError("400 Bad Request: 로그인 실패")
                    elif response.status == 500:
                        raise RuntimeError("500 Internal Server Error: 서버 오류")  # 서버 오류
                    else:
                        raise RuntimeError(f"다른 응답 코드: {response.status}")  # 기타 오류
                else:
                    raise RuntimeError("페이지 로드 실패")  # 응답이 없는 경우

                #####################################4번째 주석 풀어아햠(API 응답 대기 코드)########################################################
                # # 데이터 수집 객체 생성 및 설정
                # data_collect=AccountDataCollector(page, context,taget_url_total,target_columns,banner_tag,banner_link_tag,consent_file_path)
                # await data_collect.setup_response_handler()  # 응답 핸들러 설정
                # await page.wait_for_timeout(4000)  # 4초 대기
                
                #########################################3번째 주석 풀어아햠(인증 관련 코드)#################################################################
                #try:
                #    # 인증 관련 버튼 클릭 (필요한 경우)
                #    await page.locator("button[type='button']").nth(1).click(timeout=5000)
                #    
                #except:
                #    pass  # 인증이 필요하지 않은 경우 무시
                ##########################################################################################################
                #####################################4번째 주석 풀어아햠(API 응답 대기 코드)########################################################
                # # API 응답 대기
                # try:
                #     await data_collect.wait_for_responses(timeout=60)  # 60초 동안 모든 API 응답 대기
                # except asyncio.TimeoutError:
                #     print("타임아웃 발생")  # 타임아웃 발생 시
                #     for key, received in data_collect.called.items():
                #         if not received:
                #             print(f" - {key} 응답 없음")  # 응답이 없는 API 출력
                            
                # # API 응답 데이터 처리
                # row_data = await data_collect.process_responses(row)
                

                #####################################5번째 주석 풀어아햠(API 응답 대기 코드)########################################################    
                # #해당 함수는 실제 데이터가 바인딩이 완료될 때까지 대기하는 함수
                # #즉 selector안 요소를 변수로 받고 해당 변수값에 '{{' 텍스트가 없다는 것은 바인딩이 완료되었다는 뜻 이후 데이터 반환
                # await page.wait_for_function(
                #     """selector => {
                #         const el = document.querySelector(selector);
                #         return el && !el.innerText.includes("{{");
                #     }""",
                #     arg=[main_headline_tag],  # ✅ Python 변수 전달
                #     timeout=80000  # 80초 타임아웃
                # )



                # # HTML 데이터 추출
                # html_parse_data = htmlExtractor(page,main_headline_tag, main_desc_tag,story_data_tag,row_data, target_columns)
                # await html_parse_data.html_main_headline_ext()  # 메인 헤드라인 추출
                # await html_parse_data.html_main_description_ext()  # 메인 설명 추출
                # await html_parse_data.html_story_data_ext()  # 스토리 데이터 추출

                # # 결과 데이터를 DataFrame에 추가
                # main_result.loc[len(main_result)] = row_data
                ################################################################################################################
                await page.wait_for_timeout(2000)  # 2초 대기
                #해당 페이지 캡처
                await page.screenshot(path=result_full_path+'\\'+str(row['Account'])+'.png', full_page=True)  # 전체 페이지 스크린샷

                # 정상 종료 및 리소스 정리
                await page.wait_for_timeout(2000)  # 2초 대기
                await page.close()  # 페이지 닫기
                await context.close()  # 컨텍스트 닫기
                await browser.close()  # 브라우저 닫기

                # 성공했으므로 재시도 루프 종료
                break

            except Exception as e:
                print(f"일반 예외 발생 (시도 {attempt}/3) :", e)  # 예외 발생 시 출력
                # 리소스 정리 (있을 경우에만)
                try:
                    if page:
                        await page.close()
                except:
                    pass
                try:
                    if context:
                        await context.close()
                except:
                    pass
                try:
                    if browser:
                        await browser.close()
                except:
                    pass

                # 마지막(3회차) 실패 시 에러 행 기록
                if attempt == 3:
                    error_row = {col: '없음' for col in main_result.columns}
                    error_row['Account'] = row['Account']
                    error_row['country_code'] = row['country_code']
                    main_result.loc[len(main_result)] = error_row  # 에러 행을 결과에 추가
                else:
                    # 다음 재시도 전 잠시 대기
                    await asyncio.sleep(2)

async def main():
    """
    메인 함수 - Playwright 실행 및 run 함수 호출
    """
    async with async_playwright() as playwright:
        await smartThings_main(playwright)  # run 함수 실행
        
asyncio.run(main())  # 비동기 실행






# rowdata_excel.contents_mapping()  # 콘텐츠 매핑
# # 우산 매핑 및 최종 결과 생성
# rowdata_excel.umbrella_main_mapping(main_result,country_codes)  # 우산 파일을 사용한 메인 데이터 매핑
# final_format_result = rowdata_excel.get_result()  # 최종 포맷 결과 가져오기

# # 결과 파일 저장
# final_format_result.to_excel(r'C:\Users\WW\Desktop\테스트_결과_format.xlsx', index=False, sheet_name='테스트결과')  # 포맷 결과 저장
# main_result.to_excel(r'C:\Users\WW\Desktop\테스트_결과_main.xlsx', index=False, sheet_name='테스트결과')  # 메인 결과 저장
