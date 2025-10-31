import pandas as pd

class product:
    """
    삼성 제품 데이터를 처리하고 우선순위에 따라 정렬하는 클래스
    
    - 제품 데이터와 메타데이터를 받아서 처리
    - 등록 채널과 등록 상태에 따른 우선순위 설정
    - 정렬된 제품 목록에서 상위 2개 제품명 반환
    """
    
    def __init__(self, meta_data, product_data):
        """
        product 클래스 초기화
        
        Args:
            meta_data: 제품 메타데이터 딕셔너리 (modelCode를 키로 사용)
            product_data: 제품 데이터 리스트 (API 응답에서 받은 제품 정보들)
        """
        self.meta_data = meta_data  # 제품 메타데이터 (modelCode -> 제품 정보 매핑)
        self.product_data = product_data  # 원본 제품 데이터 리스트
        self.target_columns = [    
        'modelCode',      # 제품 모델 코드
        'registration',    # 등록 상태 (REGISTRATION, UNREGISTRATION 등)
        'channel',        # 등록 채널 (SAMSUNG_ACCOUNT, SMARTTHINGS 등)
        'createdDateTime' # 생성 날짜/시간
        ]

    def get_priority(row):
        """
        제품의 우선순위를 결정하는 정적 메서드
        
        Args:
            row: 제품 데이터 행 (DataFrame의 한 행)
            
        Returns:
            int: 우선순위 (1: 최고, 2: 중간, 3: 최저)
            
        우선순위 규칙:
        1. SAMSUNG_ACCOUNT 채널 + REGISTRATION 상태 (최고 우선순위)
        2. REGISTRATION 상태 (중간 우선순위)
        3. 기타 모든 경우 (최저 우선순위)
        """
        if row['channel'] == 'SAMSUNG_ACCOUNT' and row['registration'] == 'REGISTRATION':
            return 1  # 최고 우선순위: 삼성 계정으로 등록된 제품
        elif row['registration'] == 'REGISTRATION':
            return 2  # 중간 우선순위: 등록된 제품 (채널 무관)
        else:
            return 3  # 최저 우선순위: 미등록 제품

    def get_result(self):
        """
        제품 데이터를 처리하고 우선순위에 따라 정렬하여 상위 2개 제품명을 반환
        
        Returns:
            tuple: (product1, product2) - 상위 2개 제품명
            
        처리 과정:
        1. 제품 데이터를 DataFrame으로 변환
        2. 우선순위 계산 및 정렬
        3. 메타데이터에서 제품명 추출
        4. 상위 2개 제품명 반환
        """

        # 결과를 저장할 DataFrame 초기화
        df_product = pd.DataFrame(columns=self.target_columns)
        rows = []
        
        # 제품 데이터를 DataFrame 형태로 변환
        for value in self.product_data :
            rows.append({
                'modelCode': value.get('modelCode', '없음'),  # 모델 코드 (없으면 '없음')
                'registration': value.get('records', [{}])[0].get('type', '없음'),  # 등록 상태 (records 배열의 첫 번째 요소)
                'channel': value.get('records', [{}])[0].get('channel', '없음'),    # 등록 채널
                'createdDateTime': str(value.get('records', [{}])[0].get('createdDateTime', '없음')).split('T')[0],  # 생성 날짜 (T 이전 부분만)
            })

        # DataFrame 생성
        df_product = pd.DataFrame(rows, columns=self.target_columns)
        df_product['insertion_order'] = df_product.index  # 원본 순서 보존을 위한 컬럼 추가
        
        # priority 설정 - 각 행에 대해 우선순위 계산
        df_product['priority'] = df_product.apply(product.get_priority, axis=1)

        # 날짜 변환 - 문자열을 datetime 객체로 변환
        df_product['createdDateTime'] = pd.to_datetime(df_product['createdDateTime'])
     
        # 정렬: priority → createdDateTime → insertion_order
        # priority: 오름차순 (1이 가장 높음)
        # createdDateTime: 내림차순 (최신 날짜가 먼저)
        # insertion_order: 오름차순 (원본 순서 유지)
        df_sorted = df_product.sort_values(
            by=['priority', 'createdDateTime', 'insertion_order'],
            ascending=[True, False, True]
        ).reset_index(drop=True)
        
        # 상위 2개 제품의 메타데이터에서 제품명 추출
        for compare_code in self.meta_data:
            # 첫 번째 제품 (최고 우선순위)
            if df_sorted.at[0,'modelCode'] == compare_code:
                product1 = self.meta_data[compare_code]['nameCis']  # 첫 번째 제품명

            # 두 번째 제품 (두 번째 우선순위)
            elif df_sorted.at[1,'modelCode'] == compare_code:
                product2 = self.meta_data[compare_code]['nameCis']  # 두 번째 제품명
    
        return product1, product2  # 상위 2개 제품명 반환           
        
