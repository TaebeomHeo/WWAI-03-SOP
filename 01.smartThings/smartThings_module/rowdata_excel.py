import pandas as pd
import os
import re
pd.set_option('display.max_columns', None)
#pd.set_option('display.max_colwidth', None)

class RowDataExcel:
    """
    삼성 SmartThings 프로젝트의 Excel 데이터를 처리하는 클래스
    - Excel 파일에서 테스트 데이터를 로드하고 처리
    - 국가별 데이터 매핑 및 포맷팅
    - 최종 결과 데이터 생성
    """
    def __init__(self, row_file_path,contents_file_path,umbrella_file_path,country_code, 
                 tc_sheet_name, usecols,banner_text,banner_link_text,banner_hyperlink, header_row=2):
        """
        RowDataExcel 클래스 초기화
        
        Args:
            row_file_path: 메인 테스트 데이터 Excel 파일 경로
            contents_file_path: 콘텐츠 매핑 파일들이 저장된 디렉토리 경로
            umbrella_file_path: 우산(umbrella) 파일들이 저장된 디렉토리 경로
            country_code: 처리할 국가 코드 리스트 (예: ['DE','FR','ES','IT'])
            tc_sheet_name: Excel 시트 이름
            usecols: 사용할 Excel 컬럼 (예: 'C,U,X,Y,Z')
            banner_text: 기본 배너 텍스트
            banner_link_text: 기본 배너 링크 텍스트
            banner_hyperlink: 기본 배너 하이퍼링크
            header_row: Excel 헤더 행 번호 (기본값: 2)
        """
        self.row_file_path = row_file_path
        self.umbrella_file_path = umbrella_file_path
        self.contents_file_path = contents_file_path
        self.country_code = country_code
        self.tc_sheet_name = tc_sheet_name
        self.usecols = usecols
        self.header_row = header_row
        self.df_rowdata = None  # 원본 Excel 데이터를 저장할 DataFrame
        self.df_result = pd.DataFrame()  # 최종 결과를 저장할 DataFrame
        self.df_list = []
        self.new_row=pd.DataFrame()
        self.next_row=pd.DataFrame()
        self.banner_text = banner_text
        self.banner_link_text = banner_link_text
        self.banner_hyperlink = banner_hyperlink
        
    def load_excel(self):
        """
        Excel 파일을 로드하고 컬럼명을 리네이밍하는 함수
        
        - 지정된 Excel 파일을 읽어서 DataFrame으로 저장
        - 컬럼명을 의미있는 이름으로 변경 (storyIdRank1, main_headline 등)
        """
        self.df_rowdata = pd.read_excel(
            self.row_file_path,
            sheet_name=self.tc_sheet_name,
            header=self.header_row,
            usecols=self.usecols
        )

        
        # 컬럼 이름 리네이밍 - Excel의 실제 컬럼 위치에 따라 매핑
        self.df_rowdata.rename(columns={

            self.df_rowdata.columns[1]: 'storyIdRank1',  # 두 번째 컬럼을 storyIdRank1로 변경
             self.df_rowdata.columns[2]: 'storyIdRank1N',  # 두 번째 컬럼을 storyIdRank1로 변경
            self.df_rowdata.columns[3]: 'main_headline',  # 세 번째 컬럼을 main_headline로 변경
            self.df_rowdata.columns[4]: 'main_description1',  # 네 번째 컬럼을 main_description1로 변경
            self.df_rowdata.columns[5]: 'main_description2'  # 다섯 번째 컬럼을 main_description2로 변경
            
        }, inplace=True)
       

    def process_rows(self, max_rows=2):
        """
        Excel 행 데이터를 처리하여 결과 DataFrame을 생성하는 함수
        
        Args:
            max_rows: 처리할 최대 행 수 (기본값: 2)
            
        동작 과정:
        1. 유효한 Account가 있는 행을 찾아서 기본 행으로 설정
        2. 다음 행들을 storyIdRank2, storyIdRank3 등으로 매핑
        3. 필요한 모든 컬럼을 생성하고 기본값 설정
        """
        story_prefix = 'storyIdRank'  # 스토리 ID 접두사
        num = 1  # 스토리 순번

        #차후에 min 날려버려야 함 - 현재는 max_rows만큼만 처리
        for i in range(min(max_rows, len(self.df_rowdata))):
            
            row = self.df_rowdata.iloc[i]  # 현재 행 데이터
            
            if pd.notna(row['Account']) and row['Account'] != "":  # 유효한 데이터 행 (Account가 비어있지 않음)
               
                # 줄바꿈 문자를 공백으로 치환하여 데이터 정리
                row = row.map(lambda x: x.replace('\n', ' ') if isinstance(x, str) else x)
                self.new_row = pd.DataFrame([row])
            
                # 결과 DataFrame에 새 행 추가
                self.df_result = pd.concat([self.df_result, self.new_row], ignore_index=True)           
                
                num=1  # 스토리 순번 초기화
                
            else:
                # Account가 비어있는 행은 이전 행의 추가 스토리 데이터로 처리
                num += 1
                next_row = row
                story_key = f"{story_prefix}{num}"  # storyIdRank2, storyIdRank3 등
                story_keyN = f"{story_prefix}{num}N"  # storyIdRank2N, storyIdRank3N 등

                if(pd.isna(next_row['storyIdRank1']) or next_row['storyIdRank1']=='-'):
                    self.df_result.at[self.df_result.index[-1], story_key] = "없음"
                else:    
                    self.df_result.at[self.df_result.index[-1], story_key] = next_row['storyIdRank1']

                if(pd.isna(next_row['storyIdRank1N']) or next_row['storyIdRank1N']=='-'):
                    self.df_result.at[self.df_result.index[-1], story_key+'N'] = "없음"
                else:    
                    self.df_result.at[self.df_result.index[-1], story_key+'N'] = next_row['storyIdRank1N']  
             

        # 필요한 모든 컬럼을 생성하고 기본값 설정
        target_columns = [
        'storyIdRank1','storyIdRank2','storyIdRank3',
        'storyIdRank1N','storyIdRank2N','storyIdRank3N',
        'storyIdRank1_title', 'storyIdRank1_desc',
        'storyIdRank1_rec1','storyIdRank1_rec2','storyIdRank1_rec3','storyIdRank1_rec4','storyIdRank1_rec5',
        'storyIdRank2_title', 'storyIdRank2_desc',
        'storyIdRank2_rec1','storyIdRank2_rec2','storyIdRank2_rec3','storyIdRank2_rec4','storyIdRank2_rec5',
        'storyIdRank3_title', 'storyIdRank3_desc',
        'storyIdRank3_rec1','storyIdRank3_rec2','storyIdRank3_rec3','storyIdRank3_rec4','storyIdRank3_rec5',
        'lifeStyleIdRank1','lifeStyleIdRank2','Scenariokeyword1','Scenariokeyword2',
        'country_code','Device1','Device2','banner_text', 'banner_link_text','banner_hyperlink'
        ]

        # 누락된 컬럼들을 생성하고 기본값 설정
        for col in target_columns:

            if col not in self.df_result.columns:
                if col =='banner_text':
                    self.df_result[col] =  self.banner_text  # 기본 배너 텍스트 사용
                elif col == 'banner_link_text':
                    self.df_result[col] =  self.banner_link_text  # 기본 배너 링크 텍스트 사용
                elif col == 'banner_hyperlink':  
                    self.df_result[col] =  self.banner_hyperlink  # 기본 배너 하이퍼링크 사용
                else:
                    self.df_result[col] = "없음"  # 기타 컬럼은 "없음"으로 설정
                 
    def copy_format_data(self):
        """
        국가별 데이터 복사 함수
        
        - 첫 번째 국가는 원본 데이터에 그대로 적용
        - 나머지 국가들은 데이터를 복사하여 각 국가별로 생성
        - 예: DE, FR, ES, IT 4개 국가면 각 행이 4개씩 생성됨
        """
        copy_df_result = self.df_result.copy()  # 원본 데이터 복사
        for idx, country in enumerate(self.country_code):
            
            if(idx==0):
                self.df_result['country_code'] = country   # 첫 번째 국가는 원본에 적용
            else:
                copy_df_result['country_code'] = country   # 나머지 국가는 복사본에 적용
                self.df_result = pd.concat([self.df_result, copy_df_result], ignore_index=True)   
                # 결과에 추가
        

    def umbrella_main_mapping(self, main_result, country_code):
        """
        우산(umbrella) 파일을 사용하여 메인 데이터를 매핑하는 함수
        
        Args:
            main_result: 웹에서 수집된 실제 데이터 DataFrame
            country_code: 처리할 국가 코드 리스트
            
        동작 과정:
        1. 각 국가별로 해당하는 umbrella 파일을 찾음
        2. Excel 파일에서 '11. My SmartThings' 시트의 데이터를 읽음
        3. HQ Suggestion과 일치하는 데이터를 Local 버전으로 교체
        4. 템플릿 변수들을 실제 데이터로 치환 ({Name}, {Device 1} 등)
        """
       
        umbrella_list = os.listdir(self.umbrella_file_path)  # umbrella 디렉토리의 모든 파일 목록
        for country in country_code:
            # 해당 국가의 umbrella 파일 찾기
            for filename in umbrella_list:
            
                if country in filename:  # 파일명에 국가 코드가 포함되어 있으면
                    cgd_file = filename
                    break
                
            umbrella_full_path = os.path.join(self.umbrella_file_path,cgd_file)    
            #pd.ExcelFile(umbrella_full_path)
            #sheet_names = excel_file.sheet_names
            df_umbrella = pd.read_excel(
                umbrella_full_path,
                sheet_name='11. My SmartThings',  # 특정 시트에서 데이터 읽기
                header=6,  # 7번째 행을 헤더로 사용
                usecols='H,K'  # H, K 컬럼만 사용 (HQ Suggestion, To be filled by Local)
            )

            first_col = df_umbrella.columns[0]  # 첫 번째 컬럼명 가져오기
            # 공백 제거 및 정리 (데이터 매칭을 위해)
            df_umbrella[first_col] = df_umbrella[first_col].astype(str).str.replace(" ", "").str.strip()
            
            # 각 결과 행에 대해 매핑 수행
            for idx, row in self.df_result.iterrows():

                if row['country_code'] != country:  # 해당 국가가 아니면 건너뛰기
                    continue
                # 공백 제거 및 정리 (매칭을 위해)
                row = row.map(lambda x: x.replace(" ", "").strip() if isinstance(x, str) else x)

                # umbrella 데이터와 매칭하여 교체
                for um_idx, um_row in df_umbrella.iterrows():
                    # 메인 헤드라인 매핑
                    if um_row["HQ Suggestion"] == row["main_headline"]:
                        self.df_result.at[idx, "main_headline"] = um_row["To be filled by Local"]
                        
                        value = self.df_result.at[idx, "main_headline"]
                        # {Name} 템플릿을 실제 계정명으로 치환
                        #self.df_result.at[idx, "main_headline"] = value.replace("{Name}", self.df_result.at[idx, "Account"].split("@")[0])
                        self.df_result.at[idx, "main_headline"] = value.replace("{Name}", main_result.at[idx, "fullName"])
                    # 메인 설명1 매핑
                    if um_row["HQ Suggestion"] == row["main_description1"]:
                        #self.df_result.at[idx, "main_description1"] = um_row["To be filled by Local"]
                        #value = self.df_result.at[idx, "main_description1"]
                        ## 템플릿 변수들을 실제 데이터로 치환
                        #value= value.replace("{Device 1}", main_result.at[idx, "Device1"])
                        #value= value.replace("{Device 2}", main_result.at[idx, "Device2"])
                        #value= value.replace("{lifestyle1}", main_result.at[idx, "lifeStyleIdRank1"])
                        #value= value.replace("{lifestyle2}", main_result.at[idx, "lifeStyleIdRank2",])
                        #value= value.replace("{Scenario keyword 1}", main_result.at[idx, "Scenariokeyword1"])
                        #value= value.replace("{Scenario keyword 2}", main_result.at[idx, "Scenariokeyword2"])
                        #self.df_result.at[idx, "main_description1"] = value
                       
                        self.df_result.at[idx, "main_description1"] = um_row["To be filled by Local"]
                        template_mapping = {
                            "{Device 1}": main_result.at[idx, "Device1"],
                            "{Device 2}": main_result.at[idx, "Device2"],
                            "{lifestyle1}": main_result.at[idx, "lifeStyleIdRank1"],
                            "{lifestyle2}": main_result.at[idx, "lifeStyleIdRank2"],
                            "{Scenario keyword 1}": main_result.at[idx, "lifeStyleIdRank1"],
                            "{Scenario keyword 2}": main_result.at[idx, "lifeStyleIdRank2"]
                        }
        
                        # 모든 템플릿 변수 치환
                        value = self.df_result.at[idx, "main_description1"]
                        for template, replacement in template_mapping.items():
                            value  = value.replace(template, str(replacement))
                        self.df_result.at[idx,"main_description1"] = value
                            
                            # 메인 설명2 매핑
                    if um_row["HQ Suggestion"] == row["main_description2"]:
                        self.df_result.at[idx, "main_description2"] = um_row["To be filled by Local"]


                    # 배너 텍스트 매핑
                    if um_row["HQ Suggestion"] == row["banner_text"]:
                        self.df_result.at[idx, "banner_text"] = um_row["To be filled by Local"]

                    # 배너 링크 텍스트 매핑
                    if um_row["HQ Suggestion"] == row["banner_link_text"]:
                        self.df_result.at[idx, "banner_link_text"] = um_row["To be filled by Local"]

                    # 배너 하이퍼링크 매핑
                    if um_row["HQ Suggestion"] == row["banner_hyperlink"]:
                        self.df_result.at[idx, "banner_hyperlink"] = um_row["To be filled by Local"]

                # main_description1과 main_description2를 합쳐서 main_description 생성
                self.df_result.at[idx,"main_description"] = str(self.df_result.at[idx,"main_description1"])+' '+ str(self.df_result.at[idx,"main_description2"])
        

    def contents_mapping(self):
        """
        콘텐츠 파일을 사용하여 스토리 데이터를 매핑하는 함수
        
        동작 과정:
        1. contents 디렉토리의 모든 파일을 검색
        2. 각 스토리 ID에 해당하는 파일을 찾음
        3. 국가별 시트에서 해당 섹션의 제목과 설명을 추출
        4. storyIdRank1_title, storyIdRank1_desc 등에 매핑
        """
        format_list = os.listdir(self.contents_file_path)  # contents 디렉토리의 모든 파일 목록
        
        # 각 결과 행에 대해 콘텐츠 매핑 수행
        for idx, row in self.df_result.iterrows():
            
            # storyIdRank1, storyIdRank2, storyIdRank3 각각에 대해 처리
            for value in range(1,4):
                col = 'storyIdRank'+str(value)  # storyIdRank1, storyIdRank2, storyIdRank3
                col_title = col+'_title'  # storyIdRank1_title 등
                col_desc = col+'_desc'    # storyIdRank1_desc 등
                
                if not col in row: # 해당 데이터에 col 컬럼이 없으면 스킵
                    continue
                if row[col]!='없음':  # 스토리 ID가 존재하는 경우만 처리
                    
                    # 스토리 ID에서 콘텐츠 번호와 섹션 번호 추출 (예: "1-2" -> story_con_num=1, story_sec_num=2)
                    story_con_num, story_sec_num = row[col].split('-')
                   
                else:
                    continue  # 스토리 ID가 없으면 건너뛰기

                # contents 디렉토리의 모든 파일을 검색하여 매칭되는 파일 찾기
                for filename in format_list:

                    # 파일명에서 숫자 추출 (예: "format001.xlsx" -> 1)
                    match = re.search(r'(\d+)$', os.path.splitext(filename)[0]) # 숫자추출
                   
                    if match:
                        file_num = int(match.group(1).lstrip("0")) # 앞의 0 제거 후 정수로 변환
                        
                        # 파일 번호와 콘텐츠 번호가 일치하는 경우
                        if file_num == int(story_con_num):
                            
                            format_full_path = os.path.join(self.contents_file_path,filename)
                            excel_file = pd.ExcelFile(format_full_path)
                            
                            sheet_names = excel_file.sheet_names

                            # 국가별 시트 찾기
                            for sheet in sheet_names:
                               
                                if row["country_code"] in sheet:  # 시트명에 국가 코드가 포함되어 있으면
                                    matched_sheet = sheet

                                    # C 컬럼만 읽어오기
                                    df_format_data = pd.read_excel(format_full_path, sheet_name=sheet, usecols='c')
                                    
                                    
                                    # 섹션 번호에 따라 다른 행에서 데이터 추출
                                    if int(story_sec_num) ==1:  # 섹션 1
                                        sec1_title = df_format_data.iloc[8].values[0]   # 9번째 행의 제목
                                        sec1_desc = df_format_data.iloc[9].values[0]    # 10번째 행의 설명
                                      
                                        self.df_result.at[idx, col_title] = sec1_title
                                        self.df_result.at[idx,col_desc] = sec1_desc
                                        
                                    elif int(story_sec_num) ==2:  # 섹션 2
                                        sec2_title = df_format_data.iloc[13].values[0]  # 14번째 행의 제목
                                        sec2_desc = df_format_data.iloc[14].values[0]   # 15번째 행의 설명
                                        self.df_result.at[idx,col_title] = sec2_title
                                        self.df_result.at[idx,col_desc] = sec2_desc
                                    else:  # 섹션 3
                                        sec3_title = df_format_data.iloc[18].values[0]  # 19번째 행의 제목
                                        sec3_desc = df_format_data.iloc[19].values[0]   # 20번째 행의 설명
                                        self.df_result.at[idx,col_title] = sec3_title
                                        self.df_result.at[idx, col_desc] = sec3_desc
                            
                            excel_file.close()
                            break
    def get_result(self):
        """
        최종 처리된 결과 DataFrame을 반환하는 함수
        
        Returns:
            pd.DataFrame: 모든 처리가 완료된 최종 결과 데이터
        """
        return self.df_result

