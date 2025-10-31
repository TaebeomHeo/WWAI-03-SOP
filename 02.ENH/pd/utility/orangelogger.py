"""
orangelogger.py - 고성능 로깅 시스템

OrangeClient 및 외부 애플리케이션에서 사용 가능한 고성능 로깅 시스템입니다.
BaseLogger 클래스를 상속하여 싱글톤 패턴으로 구현된 로거를 사용하는 것을 권장합니다.

환경 및 전제 조건:
- Windows 환경, Python 3.11.9 기준으로 동작합니다.
- 모든 콘솔 출력은 Logger를 통해 수행하며, 로깅 메시지는 영어로 기록합니다.

실행 흐름 요약:
- 최초 접근 시 환경 변수에서 레벨을 읽어 포맷터/핸들러를 구성 → 호출 모듈명 자동 탐지 → 콘솔/파일 이중 출력

주요 기능:
- 자동 모듈명 인식 및 캐싱 (호출 스택 분석)
- 레벨별 컬러 헤더 지원 ([ ] 부분만)
- 이중 출력 (콘솔: 컬러, 파일: 일반 텍스트)
- 실행당 단일 로그 파일 생성 (경로 캐싱)
- 환경변수를 통한 콘솔/파일 로그 레벨 개별 설정
  - LOG_LEVEL: 콘솔 로그 레벨 (기본값: debug)
  - FILE_LOG_LEVEL: 파일 로그 레벨 (기본값: LOG_LEVEL과 동일)
- 외부 의존성 없음 (표준 라이브러리만 사용)

사용 방법:
BaseLogger는 직접 사용하지 않고, 항상 상속을 통해 싱글톤 패턴으로 구현하여 사용합니다.

예시:
```python
from services.orangelogger import BaseLogger

class MyLogger(BaseLogger):
    # 싱글톤 인스턴스
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MyLogger, cls).__new__(cls)
        return cls._instance

# 싱글톤 인스턴스 생성
log = MyLogger()

# 실제 사용 예시
log.info("PD 페이지 검증 시작")
log.debug(f"현재 URL: {page.url}")
log.warning("쿠키 동의 버튼을 찾을 수 없음")

# 에러 로깅 (스택 추적 포함)
try:
    await page.click(selector)
except Exception as e:
    log.error(f"요소 클릭 실패: {e}", exc_info=True)
```

필요에 따라 기능을 확장할 수도 있습니다:
```python
class EnhancedLogger(BaseLogger):
    # 싱글톤 인스턴스
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnhancedLogger, cls).__new__(cls)
        return cls._instance
    
    # 추가 기능 구현
    def log_with_timestamp(self, level, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        getattr(self, level)(f"[{timestamp}] {message}")
```

외부 애플리케이션에서 사용할 경우, 이 파일을 복사하여 위와 같이 BaseLogger를 상속한
싱글톤 클래스를 구현하면 됩니다.
"""

import logging
from os import makedirs, getenv, path
from inspect import currentframe
from datetime import datetime


class BaseLogger:
    """통합 로거 클래스의 기본 구현
    
    기능:
    - [ ] 부분에 레벨별 컬러 적용 (콘솔만, 파일은 일반 텍스트)
    - 자동 모듈명 인식 및 캐싱 (호출 스택 분석)
    - 로그 파일 경로 캐싱으로 실행당 단일 파일 사용
    - 콘솔/파일 로그 레벨 개별 설정 (환경변수 기반)
      - LOG_LEVEL: 콘솔 로그 레벨 (기본값: debug)
      - FILE_LOG_LEVEL: 파일 로그 레벨 (기본값: LOG_LEVEL과 동일)
    - 로그 메시지 포맷 일관성 유지 (레벨명 정규화)
    - 로거 인스턴스 캐싱으로 성능 최적화
    """
    
    # 상수 정의
    LEVELS = {"debug": 10, "info": 20, "warning": 30, "error": 40, "critical": 50}
    NAMES = {"DEBUG": "DEBUG", "INFO": "INFO ", "WARNING": "WARN ", "ERROR": "ERROR", "CRITICAL": "CRIT "}
    COLORS = {
        "DEBUG": "\033[90m", "INFO": "\033[32m", "WARNING": "\033[33m",
        "ERROR": "\033[31m", "CRITICAL": "\033[35m", "RESET": "\033[0m"
    }
    FORMAT_STR = "[%(asctime)s %(levelname)s %(name)s:%(lineno)d] %(message)s"
    DATE_FORMAT = "%y-%m-%d %H:%M:%S"
    
    def __init__(self):
        """
        BaseLogger 생성자 - 로거 속성 초기화
        """
        # 인스턴스 속성 초기화
        self.loggers = {}
        self._name_cache = {}
        self._formatters = {}
        self._logfile_path = None
        
        # 환경변수에서 로그 레벨 직접 확인하여 프로퍼티로 설정
        console_level_name = getenv("LOG_LEVEL", "debug").lower()
        file_level_name = getenv("FILE_LOG_LEVEL", console_level_name).lower()
        
        # 레벨 이름을 숫자 값으로 변환
        self.console_log = self.LEVELS.get(console_level_name, 10)  # 기본값 DEBUG
        self.file_log = self.LEVELS.get(file_level_name, self.console_log)
        
        # 로그 레벨 정보 출력
        console_level_display = next((k for k, v in self.LEVELS.items() if v == self.console_log), "debug")
        file_level_display = next((k for k, v in self.LEVELS.items() if v == self.file_log), "debug")
        
        print(f"[Logger] Console: {console_level_display.upper()}, File: {file_level_display.upper()}")
    
    def _name(self) -> str:
        """호출한 모듈의 이름을 캐시된 방식으로 추출
        
        두 단계 이전 호출 프레임에서 __file__ 값을 가져와 상대 경로로 변환
        동일 파일에서의 반복 호출 성능 개선을 위해 결과 값을 캐시함
        
        Returns:
            str: 호출한 모듈의 상대 경로 (확장자 제외)
        """
        frame = currentframe().f_back.f_back
        file = frame.f_globals.get("__file__", "")
        
        if file in self._name_cache:
            return self._name_cache[file]
        
        if not file or not file.endswith('.py'):
            name = "-"
        else:
            try:
                name = path.splitext(path.relpath(file))[0].replace(path.sep, "/")
            except:
                name = path.splitext(path.basename(file))[0]
        
        self._name_cache[file] = name
        return name
    
    @staticmethod
    def _normalize_levelname(record) -> None:
        """레벨명을 정규화하여 일관된 길이로 맞춤
        
        로깅 레벨명을 고정된 길이(5자리)로 정규화하여 로그 출력 형식 정렬
        예: 'INFO' -> 'INFO ', 'WARNING' -> 'WARN '
        
        Args:
            record: 로깅 레코드 객체
        """
        record.levelname = BaseLogger.NAMES.get(record.levelname, record.levelname[:5])
    
    def _get_formatters(self) -> tuple:
        """콘솔용(컬러)과 파일용(일반) 포맷터를 반환
        
        콘솔 출력용 컬러 포맷터와 파일 출력용 일반 텍스트 포맷터를 생성
        성능 최적화를 위해 최초 생성 후 캐싱하여 재사용
        
        Returns:
            tuple: (콘솔용 포맷터, 파일용 포맷터)
        """
        if not self._formatters:
            class ConsoleFormatter(logging.Formatter):
                def format(self, record):
                    orig_level = record.levelname
                    BaseLogger._normalize_levelname(record)
                    formatted = super().format(record)
                    
                    # [ ] 부분에만 컬러 적용
                    bracket_end = formatted.find(']')
                    if bracket_end != -1:
                        color = BaseLogger.COLORS.get(orig_level, "")
                        if color:
                            header = formatted[:bracket_end + 1]
                            message = formatted[bracket_end + 1:]
                            return f"{color}{header}{BaseLogger.COLORS['RESET']}{message}"
                    return formatted
            
            class FileFormatter(logging.Formatter):
                def format(self, record):
                    BaseLogger._normalize_levelname(record)
                    return super().format(record)
            
            self._formatters = {
                'console': ConsoleFormatter(self.FORMAT_STR, self.DATE_FORMAT),
                'file': FileFormatter(self.FORMAT_STR, self.DATE_FORMAT)
            }
        
        return self._formatters['console'], self._formatters['file']
    
    def _create_handler(self, handler_type: str, **kwargs) -> logging.Handler:
        """핸들러를 생성하고 설정
        
        핸들러 유형에 따라 콘솔 또는 파일 핸들러를 생성하고 포맷터 및 로그 레벨 설정
        
        Args:
            handler_type: 'console' 또는 'file'
            **kwargs: 파일 핸들러 생성시 전달할 추가 인자 (filename, encoding 등)
            
        Returns:
            logging.Handler: 구성된 로깅 핸들러
        """
        if handler_type == 'console':
            handler = logging.StreamHandler()
            formatter = self._get_formatters()[0]
            log_level = self.console_log
        else:  # file
            handler = logging.FileHandler(**kwargs)
            formatter = self._get_formatters()[1]
            log_level = self.file_log
        
        handler.setFormatter(formatter)
        handler.setLevel(log_level)  # 핸들러 타입에 따라 다른 레벨 적용
        return handler
        
    def _make(self, name: str) -> logging.Logger:
        """로거 인스턴스를 생성하거나 캐시에서 반환
        
        지정된 이름의 로거를 생성하거나 기존에 생성된 인스턴스를 캐시에서 반환합니다.
        
        동작 과정:
        1. 이름으로 캐시 확인, 있으면 바로 반환
        2. 없으면 새 로거 인스턴스 생성
        3. 로거 설정 (handlers 초기화, propagate 비활성화)
        4. 로그 레벨 설정 (console_log와 file_log 중 낮은 값)
        5. 콘솔 핸들러 추가
        6. 파일 핸들러 추가 (실행당 하나의 로그 파일 사용)
        7. 생성된 로거를 캐시에 저장
        
        모든 로거는 콘솔과 파일에 동시 출력되며, 파일 경로는 캐싱되어 하나의 실행에서
        모든 로거가 동일한 로그 파일을 사용합니다.
        
        Args:
            name: 로거 이름 (일반적으로 모듈 경로)
            
        Returns:
            logging.Logger: 구성된 로거 인스턴스
        """
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = False
        # 로거의 레벨은 가장 낮은 레벨로 설정 (모든 메시지 통과 후 핸들러에서 필터링)
        logger.setLevel(min(self.console_log, self.file_log))
        
        # 콘솔 핸들러 추가
        logger.addHandler(self._create_handler('console'))
        
        # 파일 핸들러 추가 (안전하게)
        try:
            # 로그 파일 경로를 캐싱하여 하나의 로그 파일만 사용
            if self._logfile_path is None:
                makedirs("logs", exist_ok=True)
                self._logfile_path = f"logs/{datetime.now():%y%m%d-%H%M%S}.log"
                
            logger.addHandler(self._create_handler('file', filename=self._logfile_path, encoding="utf-8"))
        except Exception:
            # 파일 핸들러 생성 실패시 콘솔로만 출력하되, 에러는 무시
            pass
        
        self.loggers[name] = logger
        return logger
    
    def __getattr__(self, method: str):
        """로그 메서드들을 동적으로 제공
        
        debug, info, warning, error, critical 메서드를 동적으로 처리합니다.
        각 호출 시 자동으로 호출 모듈명을 탐지하여 해당 모듈용 로거를 생성/반환합니다.
        
        동작 과정:
        1. 요청된 메서드가 유효한 로그 레벨인지 확인
        2. _name()을 통해 호출 모듈 경로 확인
        3. _make()를 통해 해당 모듈용 로거 인스턴스 생성/반환
        4. 요청된 로그 레벨 메서드 반환
        
        사용 예시:
        ```python
        from services.logger import log
        
        log.debug("디버그 메시지")
        log.info("정보 메시지")
        log.warning("경고 메시지")
        log.error("오류 메시지")
        log.critical("심각한 오류 메시지")
        ```
        
        Args:
            method: 호출된 메서드 이름
            
        Returns:
            callable: 지정된 로그 레벨의 로깅 메서드
            
        Raises:
            AttributeError: 지원하지 않는 메서드 호출 시
        """
        if method in ("debug", "info", "warning", "error", "critical"):
            return getattr(self._make(self._name()), method)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{method}'")

class Logger(BaseLogger):
    """
    싱글톤 패턴이 적용된 로거 클래스
    BaseLogger의 모든 기능을 상속하며, 애플리케이션 전체에서 단 하나의 인스턴스만 존재
    """
    
    # 싱글톤 인스턴스
    _instance = None
    
    def __new__(cls):
        """
        싱글톤 패턴 구현 - 항상 동일한 인스턴스 반환
        
        Returns:
            Logger: 싱글톤 로거 인스턴스
        """
        if cls._instance is None:
            # 새 인스턴스 생성
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

log = Logger() 