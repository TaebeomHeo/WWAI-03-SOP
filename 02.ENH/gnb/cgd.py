"""
cgd.py - GNB(Global Navigation Bar) 메뉴 트리 추출 및 JSON 변환 도구

이 파일은 CGD(Contents Guide Document) 엑셀 파일에서 GNB 메뉴 구조를 추출하여 계층적 트리로 변환하고,
JSON 파일로 저장하는 기능을 제공합니다.

주요 기능:
- 엑셀 파일 내 여러 시트에서 GNB 메뉴 정보 추출
- 데이터 전처리 및 필드 매핑, 그룹화, 정렬 등 다양한 데이터 가공
- 트리 구조(ExcelGNBNode)로 변환하여 계층적 메뉴 구조 생성
- 결과를 JSON 파일로 저장
- 상세한 예외 처리 및 로깅 지원

사용 예시:
    python cgd.py --source <엑셀파일경로> --sitecode <사이트코드>
"""

from datetime import datetime
import pandas as pd
import argparse
import json
import os
import re
from utility.orangelogger import log

class CgdMenuNode:
    """
    GNB 메뉴 트리의 각 노드를 표현하는 클래스입니다.

    이 클래스는 메뉴명, URL, 타입, 분석용 텍스트, SEO용 이름, 하위 메뉴 리스트 등
    GNB 메뉴의 계층적 구조를 관리하는 데 사용됩니다.

    속성:
        node_type (str): 메뉴 타입 (L0, L1_Product, L1_Banner)
        children (list[CgdMenuNode]): 하위 메뉴 노드 리스트

        name (str): 메뉴명
        url (str): 메뉴 링크 URL
        analytics (str): 분석용 텍스트
        url_name (str): 링크 제목/SEO
    """

    def __init__(
        self,
        node_type: str = "L0",
        name: str = "",
        url: str = "",
        analytics: str = "",
        url_name: str = "",
    ):
        """
        CgdMenuNode 인스턴스를 초기화합니다.

        파라미터:
            node_type (str): 메뉴 타입
            name (str): 메뉴명
            url (str): 메뉴 URL
            analytics (str): 분석용 텍스트
            url_name (str): 링크 제목/SEO
        반환값:
            없음
        """
        self.node_type = node_type
        self.children: list["CgdMenuNode"] = []
        self.name = name
        self.url = url
        self.analytics = analytics
        self.url_name = url_name

    def add_child(self, child: "CgdMenuNode") -> None:
        """
        하위 메뉴 노드를 현재 노드의 children 리스트에 추가합니다.

        파라미터:
            child (CgdMenuNode): 추가할 하위 노드
        반환값:
            없음
        """
        self.children.append(child)

    def to_dict(self) -> dict:
        """
        현재 노드 및 하위 노드를 dict 구조로 재귀 변환합니다.

        반환값:
            dict: 노드 및 하위 노드의 계층적 딕셔너리
        """
        return {
            "node_type": self.node_type,
            "name": self.name,
            "url": self.url,
            "analytics": self.analytics,
            "url_name": self.url_name,
            "children": [child.to_dict() for child in self.children],
        }


def transform_excel_to_tree(df: pd.DataFrame) -> list[CgdMenuNode]:
    """
    전처리된 DataFrame을 GNB 트리 구조(CgdMenuNode 리스트)로 변환합니다.

    동작 방식:
    - DataFrame의 각 행을 순회하며 Depth(계층) 정보를 기준으로 L0(최상위), L1(Product/Banner) 노드를 생성합니다.
    - L0 노드는 node_type="L0"으로 생성하여 roots 리스트에 추가합니다.
    - L1 노드는 node_type을 Depth 값에 따라 "L1_Product" 또는 "L1_Banner"로 지정하여, 직전 L0 노드의 children에 추가합니다.
    - 각 노드는 Name, Url, Analytics, UrlName 등 필드를 포함합니다.
    - 노드 생성 중 오류가 발생하면 에러 로그를 남기고 해당 행은 건너뜁니다.
    - 최종적으로 계층 구조가 완성된 루트 노드 리스트를 반환합니다.

    파라미터:
        df (pd.DataFrame): 전처리 및 필드 매핑이 완료된 데이터프레임

    반환값:
        list[CgdMenuNode]: 트리 구조의 루트 노드 리스트

    예외 처리:
    - 노드 생성 중 오류가 발생하면 에러 로그를 남기고 해당 행은 건너뜁니다.

    사용 예시:
        roots = transform_excel_to_tree(df)
        # roots는 CgdMenuNode 트리의 루트(L0) 노드 리스트

    데이터 구조:
    - CgdMenuNode: GNB 메뉴 트리의 각 노드를 표현하는 클래스
    """
    roots = []  # L0(최상위) 노드 리스트[]
    current_l0 = None  # 현재 L0 노드 참조

    # 각 행을 순회하며 계층 구조를 만듭니다
    for _, row in df.iterrows():
        try:
            # 모든 컬럼 문자열 처리
            row = row.apply(lambda x: str(x) if pd.notna(x) else x)
            # L0(최상위) 노드 생성
            if row["Depth"] == "0":
                l0_node = CgdMenuNode(
                    node_type="L0",
                    name=row["Name"],
                    url=row["Url"] or "",
                    analytics=row["Analytics"] or "",
                    url_name=row["UrlName"] or "",
                )
                roots.append(l0_node)
                current_l0 = l0_node
            # L1 노드 (Product/Banner) 생성
            elif row["Depth"].startswith("1") and current_l0 is not None:
                node_type = "L1_Product" if "Product" in row["Depth"] else "L1_Banner"
                l1_node = CgdMenuNode(
                    node_type=node_type,
                    name=row["Name"],
                    url=row["Url"] or "",
                    analytics=row["Analytics"] or "",
                    url_name=row["UrlName"] or "",
                )
                current_l0.add_child(l1_node)
        except Exception as e:
            # 노드 생성 중 오류 발생 시 로깅 후 다음 행으로 진행
            log.error(
                f"Error while creating node - row: {row.to_dict()}, error: {str(e)}"
            )
            continue
    return roots


def export_gnb_tree_to_json(tree_data: list[CgdMenuNode], sitecode: str) -> str:
    """
    GNB 트리 구조를 JSON 파일로 저장합니다.

    파라미터:
        tree_data (list[CgdMenuNode]): 트리 루트 노드 리스트
        sitecode (str): 사이트 코드(국가 코드)
    반환값:
        str: 저장된 파일 경로
    예외:
        저장 실패 시 예외 발생
    """
    if not tree_data:
        log.error("No data to export.")
        return None
    output_dir = "cgdstore"
    # 출력 디렉토리가 없으면 생성
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            log.error(f"Failed to create output directory: {str(e)}")
            raise
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{sitecode}_gnb_{now}.json"
    filepath = os.path.join(output_dir, filename)
    try:
        # 트리 데이터를 JSON 객체로 변환
        json_obj = {
            "extracted_at": now,
            "tree": [node.to_dict() for node in tree_data],
        }
    except Exception as e:
        log.error(f"Error while creating JSON object: {str(e)}")
        raise
    try:
        # JSON 파일로 저장
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_obj, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.error(f"Error while saving JSON file: {str(e)}")
        raise
    log.info(f"Result saved: {filepath}")
    log.info(f"Total {len(tree_data)} root nodes saved.")
    return filepath


def extract_gnb_from_excel(file_path: str, sitecode: str) -> list[CgdMenuNode]:
    """
    CGD 엑셀 파일에서 메뉴 구조를 추출하여 계층적 트리로 변환합니다.

    동작 방식(쉽게 설명):
    - 엑셀 파일에는 여러 시트(탭)가 있을 수 있습니다. 각 시트를 하나씩 차례로 살펴봅니다.
    - 각 시트에서 'Section', 'Field', 'HQ Suggestion' 같은 이름이 있는 줄(헤더)을 찾아, 그 아래부터 실제 데이터를 읽기 시작합니다.
    - 메뉴 이름, 메뉴에 연결된 주소(링크), 분석용 텍스트, SEO용 이름 등 필요한 정보를 뽑아냅니다.
    - 메뉴 정보는 아래와 같은 규칙으로 분류합니다:
        * 'Menu label' 또는 'Menu label (PC)'라는 항목은 메뉴의 이름입니다.
        * 'Linked URL'은 메뉴를 눌렀을 때 이동하는 주소입니다.
        * 'Text for Analytics'는 분석에 쓰이는 이름입니다.
        * 'Linked Title /SEO'는 검색엔진에 노출되는 이름입니다.
    - 같은 메뉴에 대한 여러 정보(이름, 주소 등)는 하나로 묶어서 정리합니다.
    - 메뉴의 깊이(계층)는 'Depth'라는 값을 보고 판단합니다.
        * 'L0'로 시작하면 '최상위 메뉴'(예: TV, 냉장고 등)로 간주합니다.
        * 'L1_Product', 'L1_Banner' 등은 그 아래에 붙는 '하위 메뉴'로 간주합니다.
    - 메뉴별로 큰 메뉴(가지)와 작은 메뉴(잎사귀)를 구분해서, 나무처럼 계층 구조로 만듭니다.
    - 만약 메뉴 정보가 비어 있거나, 잘못된 데이터가 있으면 그 줄은 건너뜁니다.
    - 모든 시트에서 뽑은 메뉴 트리를 합쳐서, 사이트 전체의 메뉴 구조를 완성합니다.
    
    처리 과정:
    1. 엑셀 시트별로 헤더 행 탐지 ('Section', 'Field', 'HQ Suggestion')
    2. 메뉴 관련 데이터 추출 (Menu label, Linked URL, Analytics text 등)
    3. Depth 값으로 계층 구조 파악 (L0: 최상위, L1_*: 하위 메뉴)
    4. CgdMenuNode 객체로 트리 구조 생성

    파라미터:
        file_path (str): 엑셀 파일 경로
        sitecode (str): 사이트 코드(대문자 입력 시 소문자로 변환)

    반환값:
        list[CgdMenuNode]: 트리 루트 노드 리스트

    예외 처리:
        엑셀 파일 열기, 시트 파싱, 데이터 전처리, 트리 변환 등 모든 단계에서 오류 발생 시 에러 로그를 남기고 해당 시트/행은 건너뜁니다.
        모든 시트에서 데이터 추출에 실패하면 None 반환

    사용 예시:
        tree_data = extract_gnb_from_excel('UK_GNB.xlsx', 'UK')
        # tree_data는 CgdMenuNode 트리의 루트(L0) 노드 리스트

    데이터 구조:
        - CgdMenuNode: GNB 메뉴 트리의 각 노드를 표현하는 클래스

    (비유: 엑셀 표에서 '이 줄은 메뉴 이름, 이 줄은 주소'처럼 정해진 규칙에 따라 정보를 뽑아내고,
    큰 메뉴와 작은 메뉴를 구분해서, 나무처럼 가지와 잎사귀로 연결해주는 일입니다.)
    """
    # 1. 사이트 코드가 대문자면 소문자로 변환
    if sitecode.upper() == sitecode:
        sitecode = sitecode.lower()
    log.info(f"Processing file: {file_path}")
    log.info(f"Using sitecode: {sitecode}")
    try:
        # 2. 엑셀 파일의 시트 목록 추출
        #    - 여러 시트가 존재할 수 있으므로 전체 시트명 리스트를 가져옴
        sheet_name_list = pd.ExcelFile(file_path).sheet_names
    except Exception as e:
        log.error(f"Failed to open Excel file: {str(e)}")
        raise
    all_tree_data = []  # 전체 시트의 트리 데이터 누적
    for sheet_name in sheet_name_list:
        try:
            # 3. 시트명에서 영문/공백/&만 추출 (뷰용 시트명)
            sheet_view_name = re.search(
                r"(?P<sheet_name>[a-zA-Z\s&]+)", sheet_name
            ).group("sheet_name")
        except Exception as e:
            log.error(f"Failed to parse sheet name - {sheet_name}: {str(e)}")
            continue
        log.info(f"Processing sheet: {sheet_view_name}")
        try:
            # 4. 헤더 행 탐색 (필수 컬럼 존재 여부)
            #    - 실제 데이터가 시작되는 헤더 행을 찾기 위해 반복 탐색
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            header_row = None
            required_columns = {"Section", "Field", "HQ Suggestion"}
            for i, row in df.iterrows():
                if required_columns.issubset(set(row)):
                    header_row = i
                    break
            if header_row is None:
                log.warning(f"Skipping sheet: {sheet_view_name} (No header found)")
                continue
            # 5. 실제 데이터 읽기 (헤더 행 기준)
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
            df = df.loc[1:]  # 헤더 다음 행부터 데이터 시작
            df = df.drop(columns=["Unnamed: 0", "Unnamed: 1", "Unnamed: 2"])
            # TV&AV 시트 특수 처리 (불필요 컬럼/행 제거)
            if "TV&AV" in sheet_name:
                try:
                    df = df.drop(columns=["Unnamed: 4"])
                    df = df.rename(columns={"Unnamed: 5": "Unnamed: 4"})
                    df["Unnamed: 4"] = df["Unnamed: 4"].fillna("")
                    df = df[df["Unnamed: 4"] != "Banner 3-1"]
                    df = df[~df["Unnamed: 4"].str.startswith("Banner 3-2")]
                except Exception as e:
                    log.error(f"Error while processing TV&AV sheet: {str(e)}")
                    continue
            # 6. 컬럼명 일관성 확보 및 누락값 처리
            #    - 각 시트별로 컬럼명이 다를 수 있으므로 표준 컬럼명으로 통일
            df = df.rename(
                columns={
                    df.columns[0]: "Section",
                    df.columns[1]: "Unnamed: 4",
                    df.columns[2]: "Field",
                    df.columns[3]: "HQ Suggestion",
                    df.columns[4]: "Local",
                }
            )
            # 7. 문자열 컬럼 전처리(공백 제거)
            for col in df.select_dtypes(include=["object"]).columns:
                df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)
            # 8. 컬럼명 변경 및 결측값 보정
            df = df.rename(columns={"Section": "Depth", "Unnamed: 4": "Section"})
            df["Depth"] = df["Depth"].ffill()
            df["Section"] = df["Section"].ffill()
            # 9. Depth 값 표준화 (L0/L1 등)
            df["Depth"] = df["Depth"].apply(
                lambda x: (
                    "0"
                    if str(x).startswith("L0")
                    else (
                        "1_Product"
                        if "Product" in str(x)
                        else ("1_Banner" if "Banner" in str(x) else x)
                    )
                )
            )
            # 10. 원본 순서 보존
            df["Original_Order"] = range(len(df))
            # 11. 추출 대상 필드 정의 및 필터링
            target_fields = [
                "Menu label",
                "Menu label (PC)",
                "Text for Analytics",
                "Text for Analytics (PC)",
                "Linked URL",
                "Linked Title /SEO",
            ]
            try:
                # 필수 필드만 필터링
                df_filtered = df[df["Field"].isin(target_fields)][
                    [
                        "Original_Order",
                        "Depth",
                        "Section",
                        "Field",
                        "HQ Suggestion",
                        "Local",
                    ]
                ]
            except Exception as e:
                log.error(f"Error during data filtering: {str(e)}")
                continue
            try:
                # 12. 각 필드별 데이터 매핑 (Local 우선, 없으면 HQ Suggestion)
                df_filtered["Name"] = df_filtered.apply(
                    lambda row: (
                        row["Local"]
                        if (
                            row["Field"] in ["Menu label", "Menu label (PC)"]
                            and pd.notna(row["Local"])
                        )
                        else (
                            row["HQ Suggestion"]
                            if row["Field"] in ["Menu label", "Menu label (PC)"]
                            else None
                        )
                    ),
                    axis=1,
                )
                df_filtered["Analytics"] = df_filtered.apply(
                    lambda row: (
                        row["Local"]
                        if (
                            row["Field"]
                            in ["Text for Analytics", "Text for Analytics (PC)"]
                            and pd.notna(row["Local"])
                        )
                        else (
                            row["HQ Suggestion"]
                            if row["Field"]
                            in ["Text for Analytics", "Text for Analytics (PC)"]
                            else None
                        )
                    ),
                    axis=1,
                )
                df_filtered["Url"] = df_filtered.apply(
                    lambda row: (
                        row["Local"]
                        if (row["Field"] == "Linked URL" and pd.notna(row["Local"]))
                        else (
                            row["HQ Suggestion"]
                            if row["Field"] == "Linked URL"
                            else None
                        )
                    ),
                    axis=1,
                )
                df_filtered["UrlName"] = df_filtered.apply(
                    lambda row: (
                        row["Local"]
                        if (
                            row["Field"] == "Linked Title /SEO"
                            and pd.notna(row["Local"])
                        )
                        else (
                            row["HQ Suggestion"]
                            if row["Field"] == "Linked Title /SEO"
                            else None
                        )
                    ),
                    axis=1,
                )
            except Exception as e:
                log.error(f"Error during field mapping: {str(e)}")
                continue
            try:
                # 13. 메뉴 라벨 기준 그룹화 (각 메뉴별 정보 통합)
                df_filtered["Group"] = (
                    df_filtered["Field"].isin(["Menu label", "Menu label (PC)"])
                ).cumsum()
                df_grouped = (
                    df_filtered.groupby("Group", sort=False)
                    .agg(
                        {
                            "Original_Order": "min",
                            "Depth": "first",
                            "Section": "first",
                            "Name": lambda x: next((i for i in x if pd.notna(i)), ""),
                            "Analytics": lambda x: next(
                                (i for i in x if pd.notna(i)), ""
                            ),
                            "Url": lambda x: next((i for i in x if pd.notna(i)), ""),
                            "UrlName": lambda x: next(
                                (i for i in x if pd.notna(i)), ""
                            ),
                        }
                    )
                    .reset_index(drop=True)
                )
            except Exception as e:
                log.error(f"Error during data grouping: {str(e)}")
                continue
            # 14. 빈 노드(모든 필드가 비어있는 경우) 제외
            df_grouped = df_grouped[
                df_grouped.apply(
                    lambda row: any(
                        [row["Name"], row["Url"], row["Analytics"], row["UrlName"]]
                    ),
                    axis=1,
                )
            ]
            try:
                # 15. Depth 기준 정렬 (L0 → L1_Product → L1_Banner)
                depth_order = {"0": 0, "1_Product": 1, "1_Banner": 2}
                df_grouped["Depth_Order"] = df_grouped["Depth"].map(depth_order)
                df_grouped = df_grouped.sort_values(
                    ["Depth_Order", "Original_Order"]
                ).drop(columns=["Depth_Order"])
            except Exception as e:
                log.error(f"Error during data sorting: {str(e)}")
                continue
            # 16. 트리 구조 변환 및 누적
            sheet_tree_data = transform_excel_to_tree(df_grouped)
            all_tree_data.extend(sheet_tree_data)
            log.info(f"Successfully processed sheet: {sheet_view_name}")
        except Exception as e:
            log.error(f"Error while processing sheet - {sheet_view_name}: {str(e)}")
            continue
    if not all_tree_data:
        log.error("No data extracted.")
        return None
    log.info(f"Total number of root nodes extracted: {len(all_tree_data)}")
    return all_tree_data


def main() -> None:
    """
    커맨드라인 인자를 받아 GNB 데이터 추출 및 JSON 저장을 수행하는 메인 함수입니다.

    파라미터:
        없음 (명령줄 인자 사용)
    반환값:
        없음
    예시:
        python cgd.py --source sample.xlsx --sitecode UK
    """
    parser = argparse.ArgumentParser(description="GNB 데이터 처리 도구")
    parser.add_argument(
        "--source",
        required=True,
        help="처리할 엑셀 파일 경로 (예: 'UK_GNB CGD_S.com UX Revamp(non_shop).xlsx')",
        type=str,
    )
    parser.add_argument(
        "--sitecode",
        required=True,
        help="사이트 코드 (예: UK, DE, FR 등)",
        type=str,
    )
    args = parser.parse_args()
    if not os.path.exists(args.source):
        log.error(f"File not found: {args.source}")
        return
    try:
        tree_data = extract_gnb_from_excel(args.source, args.sitecode)
        export_gnb_tree_to_json(tree_data, args.sitecode)
    except Exception as e:
        log.error(f"Error occurred during processing: {e}")


if __name__ == "__main__":
    main()
