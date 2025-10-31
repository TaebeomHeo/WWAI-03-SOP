"""
utils.py - 범용 문자열/URL 정제 및 비교 유틸리티 모듈

이 모듈은 GNB/CGD 등 다양한 도메인에서 공통으로 사용할 수 있는 문자열 및 URL 정제, 비교 함수만을 제공합니다.
- URL 표준화, 도메인 보정, 도메인 무시 비교
- 메뉴명(텍스트) 정제 및 비교(공백, 특수문자, 따옴표 등 실무 정책 반영)
- 모든 함수/클래스/주석은 한국어로 작성, 로그는 영어로만 출력
"""

from urllib.parse import urlparse, urlunparse
from utility.orangelogger import log

def standardize_url(url: str) -> str:
    """
    URL을 비교/저장에 적합하게 표준화합니다.
    (path 마지막 / 제거, 쿼리, 프래그먼트 등 모두 포함)

    예시:
        >>> standardize_url("https://site.com/shop/")
        'https://site.com/shop'
        >>> standardize_url("http://site.com/shop?ref=main")
        'http://site.com/shop?ref=main'
        >>> standardize_url("https://site.com/shop//")
        'https://site.com/shop'
        >>> standardize_url("https://site.com/shop/galaxy//?promo=1#frag")
        'https://site.com/shop/galaxy?promo=1#frag'
    """
    parsed = urlparse(url)
    normalized_path = parsed.path.rstrip('/')
    return urlunparse((parsed.scheme, parsed.netloc, normalized_path, parsed.params, parsed.query, parsed.fragment))


def refine_url(url: str, base_domain: str) -> str:
    """
    입력된 url이 도메인(netloc)이 없는 경우에만 base_domain을 붙여 새탭에서 열릴 수 있도록 보정합니다.
    도메인이 이미 포함된 경우에는 원본 url을 그대로 반환합니다.
    (즉, URL 정보를 최대한 보존하며, 도메인 없는 경우에만 최소한의 수정만 적용)
    ※ 입력 url의 앞뒤 공백 및 path 내 모든 공백(스페이스)은 자동으로 제거됩니다.

    예시:
        >>> refine_url("/shop/galaxy", "https://site.com")
        'https://site.com/shop/galaxy'
        >>> refine_url("shop/galaxy", "https://site.com")
        'https://site.com/shop/galaxy'
        >>> refine_url("https://other.com/shop/galaxy", "https://site.com")
        'https://other.com/shop/galaxy'
        >>> refine_url("http://abc.com/page", "https://site.com")
        'http://abc.com/page'
        >>> refine_url("site.com/shop", "https://site.com")
        'https://site.com/site.com/shop'
        >>> refine_url("//other.com/shop/galaxy", "https://site.com")
        '//other.com/shop/galaxy'
        >>> refine_url("/shop/공백 ", "https://site.com")
        'https://site.com/shop/공백'
        >>> refine_url("/shop/공 백 ", "https://site.com")
        'https://site.com/shop/공백'
    """
    if not url:
        return url
    url = url.strip()  # 앞뒤 공백 제거
    url = url.replace(' ', '')  # path 내 모든 공백 제거
    # 추가: //로 시작하면 base_domain에서 프로토콜을 추출해 붙여줌
    if url.startswith("//"):
        parsed_base = urlparse(base_domain)
        scheme = parsed_base.scheme or "https"
        return f"{scheme}:{url}"
    parsed = urlparse(url)
    # 도메인(netloc)이 없으면 base_domain을 붙여 절대 URL로 변환
    if not parsed.netloc:
        # 상대경로면 /로 시작하도록 보정
        if not url.startswith("/"):
            url = f"/{url}"
        return f"{base_domain.rstrip('/')}" + url
    # 도메인이 있으면 원본 url 그대로 반환
    return url


def compare_url_without_domain(left_url: str, right_url: str) -> bool:
    """
    두 URL에서 도메인(netloc)만 제외하고, 스킴, 패스, 파라미터, 쿼리, 프래그먼트가 모두 동일한지 비교합니다.
    동일하면 True, 다르면 False를 반환합니다.

    - http와 https(스킴)가 다르면 False를 반환합니다(단, 둘 중 하나라도 도메인이 없으면 scheme은 무시).
    - 두 URL 중 하나라도 도메인(netloc)이 없으면 path, params, query, fragment만 비교합니다.

    예시:
        >>> compare_url_without_domain('https://aaa.com/shop/galaxy?promo=1', 'http://bbb.com/shop/galaxy?promo=1')
        False
        >>> compare_url_without_domain('https://aaa.com/shop/galaxy', 'https://aaa.com/shop/galaxy/')
        True
        >>> compare_url_without_domain('https://aaa.com/shop/galaxy?promo=1', 'https://aaa.com/shop/galaxy?promo=2')
        False
        >>> compare_url_without_domain('https://aaa.com/shop/galaxy', '/shop/galaxy')
        True
        >>> compare_url_without_domain('/shop/galaxy', '/shop/galaxy/')
        True
    """
    if not left_url or not right_url:
        return False
    left_parsed = urlparse(left_url)
    right_parsed = urlparse(right_url)
    left_path = left_parsed.path.rstrip('/')
    right_path = right_parsed.path.rstrip('/')
    # 둘 중 하나라도 도메인(netloc)이 없으면 scheme은 무시하고 비교
    if not left_parsed.netloc or not right_parsed.netloc:
        return (
            left_path == right_path and
            left_parsed.params == right_parsed.params and
            left_parsed.query == right_parsed.query and
            left_parsed.fragment == right_parsed.fragment
        )
    # 둘 다 도메인이 있으면 scheme까지 모두 비교
    return (
        left_parsed.scheme == right_parsed.scheme and
        left_path == right_path and
        left_parsed.params == right_parsed.params and
        left_parsed.query == right_parsed.query and
        left_parsed.fragment == right_parsed.fragment
    )


def compare_name(left_name: str, right_name: str) -> bool:
    """
    두 메뉴명(left_name, right_name)을 내부에서 직접 정제(공백, 특수문자, 따옴표 등 처리)한 뒤, 값이 동일한지 여부를 반환합니다.
    - 정제 정책:
        1. 문자열 앞뒤의 공백/탭/개행 등 모두 제거 (strip)
        2. 유니코드 따옴표(‘ ’)는 일반 따옴표(')로, 유니코드 쌍따옴표(“ ”)는 일반 쌍따옴표(")로 변환
        3. 지정 특수문자(↗ 등)는 모두 제거
        4. 문자열 앞뒤의 빈칸은 최종적으로 한 번 더 strip하여 비교
    - 정제 후 둘 다 빈 문자열이면 True
    - 한쪽만 빈 문자열이면 False
    - 정제 후 값이 같으면 True, 다르면 False

    예시:
        >>> compare_name('  Galaxy S25 Ultra  ', 'Galaxy S25 Ultra')
        True
        >>> compare_name('   ', '')
        True
        >>> compare_name('↗↗↗↗', '')
        True
        >>> compare_name('abc', '')
        False
        >>> compare_name('abc', 'def')
        False
    """
    def _local_clean(text: str) -> str:
        try:
            text = str(text)
            if not text:
                return ""
            # 1. 앞뒤 공백/탭/개행 등 모두 제거
            cleaned = text.strip()
            # 2. 유니코드 따옴표/쌍따옴표 변환
            translation_table = str.maketrans({
                "“": '"', "”": '"', "‘": "'", "’": "'"
            })
            cleaned = cleaned.translate(translation_table)
            # 3. 지정 특수문자 제거 (↗ 등)
            for ch in ["↗"]:
                cleaned = cleaned.replace(ch, "")
            # 4. 최종적으로 앞뒤 공백 한 번 더 제거
            return cleaned.strip()
        except Exception as e:
            log.error(f"_local_clean exception: {e} | text={text}")
            return ""
    left_clean = _local_clean(left_name)
    right_clean = _local_clean(right_name)
    # 정제 후 둘 다 빈 문자열이면 True
    if left_clean == "" and right_clean == "":
        return True
    # 한쪽만 빈 문자열이면 False
    if left_clean == "" or right_clean == "":
        return False
    return left_clean == right_clean


if __name__ == "__main__":
    def main() -> None:
        """
        standardize_url, refine_url, compare_url_without_domain, compare_name 함수의 다양한 입력값 테스트용 메인 함수 (print 사용)
        각 비교 함수는 True/False 케이스를 50개씩, 정제 함수는 100개를 유형별로 분리해 테스트한다.
        """

        print("\n[TEST] standardize_url() 테스트 시작\n" + "-"*40)
        std_cases = [
            # 기본
            "https://site.com/shop/", "http://site.com/shop?ref=main", "https://site.com/shop//",
            # 쿼리/프래그먼트/파라미터
            "https://site.com/shop/galaxy/", "https://site.com/shop/galaxy", "https://site.com/shop/galaxy?promo=1",
            "site.com/shop/galaxy", "/shop/galaxy", "shop/galaxy", "", None,
            # 다양한 스킴
            "ftp://site.com/path/", "mailto:user@site.com", "file:///C:/path/to/file",
            # 중복 슬래시
            "https://site.com//shop//galaxy//", "http://site.com//shop//galaxy//",
            # 쿼리/프래그먼트/파라미터
            "https://site.com/shop?promo=1#frag", "https://site.com/shop#frag", "https://site.com/shop;param",
            # 기타
            "https://site.com", "http://site.com", "site.com", "/shop", "shop", "//site.com/shop",
            # 특수문자
            "https://site.com/shop/!@#", "https://site.com/shop/한글", "https://site.com/shop/공백 ",
            # 길이/복잡도
            "https://site.com/" + "a"*100, "https://site.com/" + "b"*200,
            # 기타
            "https://site.com/shop/galaxy//?promo=1#frag", "https://site.com/shop/galaxy//;param",
            "https://site.com/shop/galaxy//?promo=1;param#frag",
        ]
        for s in std_cases:
            try:
                result = standardize_url(s or "")
                print(f"입력: {repr(s)} → 결과: {repr(result)}")
            except Exception as e:
                print(f"입력: {repr(s)} → 예외 발생: {e}")

        print("\n[TEST] refine_url() 테스트 시작\n" + "-"*40)
        refine_base = "https://testdomain.com"
        refine_cases = [
            # 절대/상대/도메인
            ("/shop/galaxy", refine_base), ("shop/galaxy", refine_base), ("https://other.com/shop/galaxy", refine_base),
            ("http://abc.com/page", refine_base), ("site.com/shop", refine_base), ("//other.com/shop/galaxy", refine_base),
            ("", refine_base), (None, refine_base), ("/shop/galaxy?promo=1", refine_base), ("/shop/galaxy#section2", refine_base),
            ("/shop/galaxy/", refine_base), ("/", refine_base),
            # 다양한 도메인/스킴
            ("ftp://site.com/path", refine_base), ("mailto:user@site.com", refine_base), ("file:///C:/file", refine_base),
            # 특수문자/한글
            ("/shop/한글", refine_base), ("/shop/공백 ", refine_base),
            # 길이/복잡도
            ("/" + "a"*100, refine_base), ("/" + "b"*200, refine_base),
            # 기타
            ("/shop/galaxy//?promo=1#frag", refine_base), ("/shop/galaxy//;param", refine_base),
            ("/shop/galaxy//?promo=1;param#frag", refine_base),
            ("//samsung-climatesolutions.com/gb/b2c.html", refine_base)
        ]
        for url, base in refine_cases:
            try:
                result = refine_url(url or "", base)
                print(f"base: {base}, 입력: {repr(url)} → 결과: {repr(result)}")
            except Exception as e:
                print(f"base: {base}, 입력: {repr(url)} → 예외 발생: {e}")

        print("\n[TEST] compare_url_without_domain() True 케이스 (일치)\n" + "-"*40)
        compare_true_cases = [
            # 도메인 무시, path/쿼리/프래그먼트 일치
            ("https://aaa.com/shop/galaxy", "https://bbb.com/shop/galaxy"),
            ("https://aaa.com/shop/galaxy/", "https://bbb.com/shop/galaxy/"),
            ("/shop/galaxy", "/shop/galaxy/"),
            ("/shop/galaxy?promo=1", "/shop/galaxy?promo=1"),
            ("/shop/galaxy#frag", "/shop/galaxy#frag"),
            ("/shop/galaxy", "/shop/galaxy"),
            ("/shop/galaxy/", "/shop/galaxy"),
            ("/shop/galaxy/", "/shop/galaxy/"),
            ("/shop/galaxy?promo=1#frag", "/shop/galaxy?promo=1#frag"),
            # 다양한 스킴/쿼리/파라미터
            ("https://aaa.com/shop/galaxy?promo=1#frag", "https://bbb.com/shop/galaxy?promo=1#frag"),
            ("http://aaa.com/shop/galaxy", "http://bbb.com/shop/galaxy"),
            ("https://aaa.com/shop/galaxy", "/shop/galaxy"),
            ("http://aaa.com/shop/galaxy", "/shop/galaxy"),
            ("/shop/galaxy?promo=1;param#frag", "/shop/galaxy?promo=1;param#frag"),
            ("/shop/galaxy;param", "/shop/galaxy;param"),
            ("/shop/galaxy", "/shop/galaxy"),
            ("/shop/galaxy/", "/shop/galaxy/"),
            ("/shop/galaxy?promo=1", "/shop/galaxy?promo=1"),
            ("/shop/galaxy#frag", "/shop/galaxy#frag"),
            # 길이/복잡도
            ("/" + "a"*100, "/" + "a"*100),
            ("/" + "b"*200, "/" + "b"*200),
            # 기타
            ("/shop/한글", "/shop/한글"),
            ("/shop/공백 ", "/shop/공백 "),
            ("/shop/galaxy//?promo=1#frag", "/shop/galaxy//?promo=1#frag"),
            ("/shop/galaxy//;param", "/shop/galaxy//;param"),
            ("/shop/galaxy//?promo=1;param#frag", "/shop/galaxy//?promo=1;param#frag"),
            # 다양한 도메인/스킴
            ("https://aaa.com/shop/galaxy", "https://aaa.com/shop/galaxy/"),
            ("http://aaa.com/shop/galaxy", "http://aaa.com/shop/galaxy/"),
            ("https://aaa.com/shop/galaxy?promo=1", "https://aaa.com/shop/galaxy?promo=1"),
            ("https://aaa.com/shop/galaxy#frag", "https://aaa.com/shop/galaxy#frag"),
            ("https://aaa.com/shop/galaxy", "https://aaa.com/shop/galaxy"),
            ("https://aaa.com/shop/galaxy/", "https://aaa.com/shop/galaxy/"),
            ("https://aaa.com/shop/galaxy?promo=1#frag", "https://aaa.com/shop/galaxy?promo=1#frag"),
            ("https://aaa.com/shop/galaxy?promo=1;param#frag", "https://aaa.com/shop/galaxy?promo=1;param#frag"),
            ("https://aaa.com/shop/galaxy;param", "https://aaa.com/shop/galaxy;param"),
            ("https://aaa.com/shop/galaxy", "/shop/galaxy"),
            ("https://aaa.com/shop/galaxy/", "/shop/galaxy/"),
            ("https://aaa.com/shop/galaxy?promo=1", "/shop/galaxy?promo=1"),
            ("https://aaa.com/shop/galaxy#frag", "/shop/galaxy#frag"),
            ("https://aaa.com/shop/galaxy", "/shop/galaxy"),
            ("https://aaa.com/shop/galaxy/", "/shop/galaxy/"),
            ("https://aaa.com/shop/galaxy?promo=1#frag", "/shop/galaxy?promo=1#frag"),
            ("https://aaa.com/shop/galaxy?promo=1;param#frag", "/shop/galaxy?promo=1;param#frag"),
            ("https://aaa.com/shop/galaxy;param", "/shop/galaxy;param"),
        ]
        for url1, url2 in compare_true_cases:
            try:
                result = compare_url_without_domain(url1 or "", url2 or "")
                print(f"[True] 비교: {repr(url1)} <-> {repr(url2)} → 결과: {result}")
            except Exception as e:
                print(f"[True] 비교: {repr(url1)} <-> {repr(url2)} → 예외 발생: {e}")

        print("\n[TEST] compare_url_without_domain() False 케이스 (불일치)\n" + "-"*40)
        compare_false_cases = [
            # path 다름
            ("https://aaa.com/shop/galaxy", "https://aaa.com/shop/galaxy2"),
            ("/shop/galaxy", "/shop/galaxy2"),
            ("/shop/galaxy/", "/shop/galaxy2/"),
            ("/shop/galaxy?promo=1", "/shop/galaxy?promo=2"),
            ("/shop/galaxy#frag", "/shop/galaxy#other"),
            ("/shop/galaxy", None), (None, "/shop/galaxy"), ("", ""),
            # 스킴 다름
            ("https://aaa.com/shop/galaxy", "http://aaa.com/shop/galaxy"),
            ("https://aaa.com/shop/galaxy?promo=1", "http://bbb.com/shop/galaxy?promo=1"),
            ("https://aaa.com/shop/galaxy", "ftp://aaa.com/shop/galaxy"),
            # 쿼리/파라미터/프래그먼트 다름
            ("/shop/galaxy?promo=1", "/shop/galaxy?promo=2"),
            ("/shop/galaxy;param1", "/shop/galaxy;param2"),
            ("/shop/galaxy#frag1", "/shop/galaxy#frag2"),
            # 기타
            ("/shop/galaxy", "/shop/galaxy2"),
            ("/shop/galaxy/", "/shop/galaxy2/"),
            ("/shop/galaxy?promo=1", "/shop/galaxy?promo=2"),
            ("/shop/galaxy#frag", "/shop/galaxy#other"),
            ("/shop/galaxy", None), (None, "/shop/galaxy"), ("", ""),
            # 길이/복잡도
            ("/" + "a"*100, "/" + "b"*100),
            ("/" + "a"*200, "/" + "b"*200),
            # 특수문자/한글
            ("/shop/한글", "/shop/다름"),
            ("/shop/공백 ", "/shop/공백다름 "),
            # 기타
            ("/shop/galaxy//?promo=1#frag", "/shop/galaxy//?promo=2#frag"),
            ("/shop/galaxy//;param", "/shop/galaxy//;param2"),
            ("/shop/galaxy//?promo=1;param#frag", "/shop/galaxy//?promo=2;param#frag"),
            # 다양한 도메인/스킴
            ("https://aaa.com/shop/galaxy", "https://aaa.com/shop/galaxy2"),
            ("http://aaa.com/shop/galaxy", "http://aaa.com/shop/galaxy2"),
            ("https://aaa.com/shop/galaxy?promo=1", "https://aaa.com/shop/galaxy?promo=2"),
            ("https://aaa.com/shop/galaxy#frag", "https://aaa.com/shop/galaxy#frag2"),
            ("https://aaa.com/shop/galaxy", "/shop/galaxy2"),
            ("https://aaa.com/shop/galaxy/", "/shop/galaxy2/"),
            ("https://aaa.com/shop/galaxy?promo=1", "/shop/galaxy?promo=2"),
            ("https://aaa.com/shop/galaxy#frag", "/shop/galaxy#frag2"),
        ]
        for url1, url2 in compare_false_cases:
            try:
                result = compare_url_without_domain(url1 or "", url2 or "")
                print(f"[False] 비교: {repr(url1)} <-> {repr(url2)} → 결과: {result}")
            except Exception as e:
                print(f"[False] 비교: {repr(url1)} <-> {repr(url2)} → 예외 발생: {e}")

        print("\n[TEST] compare_name() True 케이스 (일치)\n" + "-"*40)
        name_true_cases = [
            # 공백/정제/따옴표/유니코드 따옴표
            ("  Galaxy S25 Ultra  ", "Galaxy S25 Ultra"),
            ("  \"프로모션\"  ", '"프로모션"'),
            ('"스페셜" 에디션', '"스페셜" 에디션'),
            ('  "Galaxy" S25  ', '"Galaxy" S25'),
            ('신제품', '신제품'),
            ('프로모션!@#$', '프로모션!@#$'),
            ('신제품😊', '신제품😊'),
            ('특가★', '특가★'),
            ('할인%쿠폰', '할인%쿠폰'),
            ('이벤트#1', '이벤트#1'),
            ('  "Galaxy" S25  ↗', '"Galaxy" S25'),
            ('  "Galaxy" S25  ↗↗', '"Galaxy" S25'),
            ('  "Galaxy" S25  ↗↗↗', '"Galaxy" S25'),
            ('  "Galaxy" S25  ↗↗↗↗', '"Galaxy" S25'),
            ('', ''),
            (None, None),
            ('   ', ''),
            ('\t', ''),
            ('\n', ''),
            ('↗↗↗↗↗↗↗↗↗↗', ''),
            ('↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗', ''),
            ('↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗', ''),
            ('↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗', ''),
            ('↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗↗', ''),
            ('삼성', '삼성'),
            ('Samsung', 'Samsung'),
            ('12345', '12345'),
            ('삼성123', '삼성123'),
            ('Samsung 123', 'Samsung 123'),
            ('"신제품"', '"신제품"'),
            ('신제품', '신제품'),
            ('"신제품"', '"신제품"'),
            ('신제품', '신제품'),
            ('"신제품" 할인', '"신제품" 할인'),
            ('AAAAAAAAAA', 'AAAAAAAAAA'),
            ('BBBBBBBBBB', 'BBBBBBBBBB'),
            ('CCCCCCCCCC', 'CCCCCCCCCC'),
            ('DDDDDDDDDD', 'DDDDDDDDDD'),
            ('EEEEEEEEEE', 'EEEEEEEEEE'),
            ('""""""""""', '""""""""""'),
            ('  \t메뉴\n  ', '메뉴'),
            ('  \n메뉴\t  ', '메뉴'),
            ('  \t\n메뉴\n\t  ', '메뉴'),
            ('메뉴↗↗↗↗↗', '메뉴'),
            ('메뉴@#$', '메뉴@#$'),
            ('메뉴!@#$', '메뉴!@#$'),
            ('메뉴%^&*', '메뉴%^&*'),
            ('메뉴()_+', '메뉴()_+'),
            ('메뉴-=~', '메뉴-=~'),
            ('Menu123', 'Menu123'),
            ('메뉴123', '메뉴123'),
            ('Menu메뉴123', 'Menu메뉴123'),
            ('123Menu메뉴', '123Menu메뉴'),
            ('메뉴Menu123', '메뉴Menu123'),
            ('"따옴표"테스트', '"따옴표"테스트'),
            ('메뉴""\'\'', '메뉴""\'\''),
            ('메뉴"""', '메뉴"""'),
            ("메뉴'''", "메뉴'''")
        ]

        for gnb, cgd in name_true_cases:
            try:
                result = compare_name(gnb, cgd)
                print(f"[True] 비교: {repr(gnb)} <-> {repr(cgd)} → 결과: {result}")
            except Exception as e:
                print(f"[True] 비교: {repr(gnb)} <-> {repr(cgd)} → 예외 발생: {e}")
                
        print("\n[TEST] compare_name() False 케이스 (불일치)\n" + "-"*40)
        name_false_cases = [
            # 한쪽만 빈 문자열이 되는 케이스
            ('   ', 'abc'),
            ('\t', 'abc'),
            ('\n', 'abc'),
            ('↗↗↗↗↗↗↗↗↗↗', 'abc'),
            ('abc', ''),
            ('abc', None),
            # path 다름/정제 후 불일치
            ("'신제품''↗", '신제품"'),
            ('신제품', '신제품 할인'),
            ('"신제품"', '"신제품" 할인'),
            ('신제품', '신제품 할인'),
            ('따옴표', '따옴표테스트'),
            ('"따옴표"', '"따옴표"테스트'),
            ('"따옴표" 테스트', '"따옴표"테스트'),
            ('따옴표', '따옴표테스트'),
            ('메뉴@#$', '메뉴!@#$'),
            ('메뉴!@#$', '메뉴@#$'),
            ('메뉴%^&*', '메뉴()_+'),
            ('메뉴()_+', '메뉴-=~'),
            ('메뉴-=~', '메뉴@#$'),
            ('Menu123', '메뉴123'),
            ('메뉴123', 'Menu123'),
            ('Menu메뉴123', '123Menu메뉴'),
            ('123Menu메뉴', '메뉴Menu123'),
            ('메뉴Menu123', 'Menu메뉴123'),
            ('  \t메뉴\n  ', '메뉴1'),
            ('  \n메뉴\t  ', '메뉴2'),
            ('  \t\n메뉴\n\t  ', '메뉴3'),
            ('메뉴↗↗↗↗↗', '메뉴1'),
            ('메뉴""\'\'', '메뉴""\'\'1'),
            ('메뉴"""', '메뉴"""1'),
            ("메뉴'''", "메뉴'''1")
        ]

        for gnb, cgd in name_false_cases:
            try:
                result = compare_name(gnb, cgd)
                print(f"[False] 비교: {repr(gnb)} <-> {repr(cgd)} → 결과: {result}")
            except Exception as e:
                print(f"[False] 비교: {repr(gnb)} <-> {repr(cgd)} → 예외 발생: {e}")

    main() 