import pandas as pd

class law_agree:
    """
    국가별 마케팅 동의 요건을 처리하는 클래스
    
    - Excel 파일에서 국가별 동의 요건 데이터를 로드
    - API 응답의 동의 타입을 분석하여 매핑
    - 해당 국가의 동의 요건 결과를 반환
    """
    
    def __init__(self,law_format_file ,law_agree_data,country_code):
        """
        law_agree 클래스 초기화
        
        Args:
            law_format_file: 국가별 마케팅 동의 요건 Excel 파일 경로
            law_agree_data: API 응답에서 받은 동의 데이터 (딕셔너리 또는 리스트)
            country_code: 처리할 국가 코드 (예: 'DE', 'FR', 'ES', 'IT')
        """
        self.law_format_file = law_format_file  # 동의 요건 Excel 파일 경로
        self.law_agree_data = law_agree_data    # API 응답의 동의 데이터
        self.country_code = country_code        # 국가 코드
        
        # Excel 파일 로드 (두 번째 행을 헤더로 사용)
        self.df_rowdata = pd.read_excel(
            law_format_file,
            header=1  # 두 번째 행을 헤더로 사용 (첫 번째 행은 제목일 가능성)
        )

    def get_no_data_result(self):
        """
        동의 데이터가 없는 경우 (204 No Content)의 결과를 반환하는 함수
        
        Returns:
            pandas.Series: 해당 국가의 동의 요건 결과 ('X' 또는 'O')
            
        - 모든 동의 타입이 '-'인 경우를 찾아서 해당 국가의 결과 반환
        - 동의가 불필요한 경우의 처리
        """
        # 모든 동의 타입이 '-'인 행을 찾아서 해당 국가의 결과 추출
        result = self.df_rowdata.query(f"MKT == '-' and CZSVC == '-' and CZADV == '-'")[self.country_code]
        print("데이터 없을경우 : ",result)  # 디버깅용 출력

        return result

    def get_data_result(self):
        """
        동의 데이터가 있는 경우 (200 OK)의 결과를 반환하는 함수
        
        Returns:
            pandas.Series: 해당 국가의 동의 요건 결과 ('X' 또는 'O')
            
        처리 과정:
        1. API 응답에서 동의 타입들을 추출
        2. 필요한 동의 타입들(MKT, CZSVC, CZADV)과 매핑
        3. 매칭되는 조건을 찾아서 해당 국가의 결과 반환
        """

        # 처리할 동의 타입 리스트
        law_list = ['MKT', 'CZSVC', 'CZADV']  # 마케팅, 서비스, 광고 동의 타입

        # API 응답에서 동의 타입들만 추출
        types = [item['type'] for item in self.law_agree_data]  # API 응답의 type 필드들
        
        # 결과 딕셔너리 초기화 - 각 동의 타입에 대해 매핑 결과 저장
        mapped_result = {}
        
        # 각 동의 타입에 대해 API 응답에 포함되어 있는지 확인
        for law in law_list:
            if law in types:  # API 응답에 해당 동의 타입이 있으면
                mapped_result[law] = law  # 실제 값으로 매핑
            else:  # API 응답에 해당 동의 타입이 없으면
                mapped_result[law] = '-'  # '-'로 매핑 (동의 불필요)
        
        # 매핑된 조건에 맞는 행을 찾아서 해당 국가의 결과 추출
        result = self.df_rowdata.query(f"MKT == '{mapped_result['MKT']}' and CZSVC == '{mapped_result['CZSVC']}' and CZADV == '{mapped_result['CZADV']}'")[self.country_code]
        print("데이터 있을경우 : ",result)  # 디버깅용 출력
        
        return result   
