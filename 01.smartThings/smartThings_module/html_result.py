import pandas as pd

class htmlExtractor:
    """
    웹페이지의 HTML 요소에서 데이터를 추출하는 클래스
    
    - Playwright 페이지 객체를 사용하여 HTML 요소 추출
    - 메인 헤드라인, 설명, 스토리 데이터 등을 수집
    - 추출된 데이터를 row_data 딕셔너리에 저장
    """
    
    def __init__(self, page, main_headline_tag:str,main_desc_tag:str,story_data_tag, row_data,target_columns):
        """
        htmlExtractor 클래스 초기화
        
        Args:
            page: Playwright 페이지 객체
            main_headline_tag: 메인 헤드라인을 추출할 CSS 선택자
            main_desc_tag: 메인 설명을 추출할 CSS 선택자
            story_data_tag: 스토리 데이터를 추출할 CSS 선택자
            row_data: 데이터를 저장할 딕셔너리
            target_columns: 처리할 컬럼 리스트
        """
        self.page = page
        self.main_headline_tag = main_headline_tag
        self.main_desc_tag = main_desc_tag
        self.story_data_tag = story_data_tag
        self.row_data = row_data
        self.target_columns = target_columns

    # def dataframe_make(self):
    #     """
    #     결과 데이터를 저장할 DataFrame을 생성하는 함수
        
    #     Returns:
    #         pd.DataFrame: 빈 DataFrame (target_columns로 구성)
            
    #     - 모든 필요한 컬럼을 포함한 DataFrame 구조 정의
    #     - Account, 메인 정보, 스토리 정보, 디바이스 정보, 배너 정보 등 포함
    #     """
    #     target_columns = [    
    #     'Account',    # 계정 정보
    #     'main_headline', 'main_description', 'main_description1', 'main_description2',  # 메인 정보
    #     'storyIdRank1', 'storyIdRank2', 'storyIdRank3',  # 스토리 ID
    #     'storyIdRank1_title', 'storyIdRank1_desc',  # 스토리 1 제목/설명
    #     'storyIdRank1_rec1','storyIdRank1_rec2','storyIdRank1_rec3','storyIdRank1_rec4','storyIdRank1_rec5',  # 스토리 1 추천 제품들
    #     'storyIdRank2_title', 'storyIdRank2_desc',  # 스토리 2 제목/설명
    #     'storyIdRank2_rec1','storyIdRank2_rec2','storyIdRank2_rec3','storyIdRank2_rec4','storyIdRank2_rec5',  # 스토리 2 추천 제품들
    #     'storyIdRank3_title', 'storyIdRank3_desc',  # 스토리 3 제목/설명
    #     'storyIdRank3_rec1','storyIdRank3_rec2','storyIdRank3_rec3','storyIdRank3_rec4','storyIdRank3_rec5',  # 스토리 3 추천 제품들
    #     'lifeStyleIdRank1','lifeStyleIdRank2','Scenariokeyword1','Scenariokeyword2',  # 라이프스타일 및 시나리오 키워드
    #     'country_code','Device1','Device2','banner_text', 'banner_link_text','banner_hyperlink'  # 국가, 디바이스, 배너 정보
    #     ]
    #     df = pd.DataFrame(columns=target_columns)
    #     return df
    
    async def html_main_headline_ext(self):
        """
        메인 헤드라인을 HTML에서 추출하는 함수
        
        - 지정된 CSS 선택자로 메인 헤드라인 요소들을 찾음
        - 모든 헤드라인 텍스트를 하나의 문자열로 결합
        - 추출된 데이터를 row_data에 저장
        """
        diff_data = {}  # 임시 데이터 저장 딕셔너리

        # CSS 선택자로 모든 메인 헤드라인 요소를 찾아서 텍스트 추출
        specific_text =' '.join([await elem.inner_text() for elem in await self.page.query_selector_all(self.main_headline_tag)])

        column = 'main_headline'  # 저장할 컬럼명
        if specific_text:  # 텍스트가 추출된 경우
            diff_data[column] = specific_text  # 임시 딕셔너리에 저장
            
            # target_columns에 있는 컬럼들에 대해 데이터 저장
            for col in self.target_columns:
                if col in diff_data:
                    self.row_data[col] = diff_data[col]  # row_data에 최종 저장
        else:  # 텍스트가 추출되지 않은 경우
            diff_data[column] = "없음"  # 기본값 설정
            self.row_data[col] = diff_data[column]  # row_data에 저장

    async def html_main_description_ext(self):
        """
        메인 설명을 HTML에서 추출하는 함수
        
        - 지정된 CSS 선택자로 메인 설명 요소들을 찾음
        - 모든 설명 텍스트를 하나의 문자열로 결합
        - 추출된 데이터를 row_data에 저장
        """
        diff_data = {}  # 임시 데이터 저장 딕셔너리
        #specific_text = await page.all_inner_texts(tag)  # 주석 처리된 다른 방법
        
        # CSS 선택자로 모든 메인 설명 요소를 찾아서 텍스트 추출
        specific_text = ' '.join([await elem.inner_text() for elem in await self.page.query_selector_all(self.main_desc_tag)])
        column = 'main_description'  # 저장할 컬럼명
        
        if specific_text:  # 텍스트가 추출된 경우

            diff_data[column] = specific_text  # 임시 딕셔너리에 저장

            # target_columns에 있는 컬럼들에 대해 데이터 저장
            for col in self.target_columns:
                if col in diff_data:
                    self.row_data[col] = diff_data[col]  # row_data에 최종 저장
        else:  # 텍스트가 추출되지 않은 경우
            diff_data[column] = "없음"  # 기본값 설정
            self.row_data[col] = diff_data[column]  # row_data에 저장


    async def html_story_data_ext(self):
        """
        스토리 데이터를 HTML에서 추출하는 함수
        
        - 스토리 섹션의 모든 요소를 찾아서 처리
        - 각 스토리의 제목, 설명, 추천 제품들을 추출
        - 추출된 데이터를 row_data에 저장
        
        처리 과정:
        1. 스토리 데이터 태그로 모든 스토리 섹션 찾기
        2. 각 스토리별로 제목, 설명, 추천 제품 추출
        3. 추출된 데이터를 적절한 컬럼명으로 저장
        """
        diff_data = {}  # 임시 데이터 저장 딕셔너리

        # 스토리 데이터 태그로 모든 스토리 섹션 찾기
        top_tag = self.page.locator(self.story_data_tag)
        count = await top_tag.count()  # 스토리 섹션 개수 확인

        if top_tag:  # 스토리 섹션이 존재하는 경우

            # 각 스토리 섹션에 대해 처리
            for i in range(count):
                top_tag_value = top_tag.nth(i)  # i번째 스토리 섹션

                # 스토리 제목 추출
                story_headline = await top_tag_value.locator('h3[class="myd26-my-story-st__headline"]').all_inner_texts()
                if story_headline:  # 제목이 존재하는 경우
                    for value in story_headline:
                        column = f'storyIdRank{i+1}_title'  # 컬럼명 생성 (예: storyIdRank1_title)

                        diff_data[column] = value  # 임시 딕셔너리에 저장

                # 스토리 설명 추출
                story_desc = await top_tag_value.locator('p[class="myd26-my-story-st__description"]').all_inner_texts()
                if story_desc:  # 설명이 존재하는 경우
                    for value in story_desc:
                        column = f'storyIdRank{i+1}_desc'  # 컬럼명 생성 (예: storyIdRank1_desc)

                        diff_data[column] = value  # 임시 딕셔너리에 저장

                # 스토리 추천 제품 추출
                story_product = await top_tag_value.locator('p[class="myd26-my-story-st__product-name"]').all_inner_texts()
                if story_product:  # 추천 제품이 존재하는 경우
                    for idx, value in enumerate(story_product, start=1):  # 1부터 시작하는 인덱스
                        column = f'storyIdRank{i+1}_rec{idx}'  # 컬럼명 생성 (예: storyIdRank1_rec1)
                        diff_data[column] = value  # 임시 딕셔너리에 저장            

            # 모든 추출된 데이터를 row_data에 저장
            for col in self.target_columns:
                if col in diff_data:
                    self.row_data[col] = diff_data[col]  # row_data에 최종 저장  