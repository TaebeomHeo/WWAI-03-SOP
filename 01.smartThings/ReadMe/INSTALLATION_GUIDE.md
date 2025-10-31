# Playwright 설치 가이드

## 개요
이 가이드는 Playwright를 사용하기 위해 필요한 모든 소프트웨어와 라이브러리를 설치하는 방법을 설명합니다.

## 시스템 요구사항

### 운영체제
- **Windows**: Windows 10 이상 (64비트)
- **macOS**: macOS 10.15 (Catalina) 이상
- **Linux**: Ubuntu 18.04, CentOS 7, 또는 호환되는 배포판

### 하드웨어
- **RAM**: 최소 4GB (8GB 권장)
- **저장공간**: 최소 2GB 여유 공간
- **CPU**: 최소 2코어 (4코어 권장)

## 1. Python 설치

### 1.1 Python 다운로드
1. [Python 공식 웹사이트](https://www.python.org/downloads/) 방문
2. 최신 Python 3.8 이상 버전 다운로드 (Python 3.11 또는 3.12 권장)
3. 운영체제에 맞는 설치 파일 선택

### 1.2 Windows에서 Python 설치
```bash
# 설치 파일 실행 후 다음 옵션 선택
☑️ Add Python to PATH
☑️ Install for all users (권장)
```

### 1.3 macOS에서 Python 설치
```bash
# Homebrew 사용 (권장)
brew install python

# 또는 공식 설치 파일 사용
```

### 1.4 Linux에서 Python 설치
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install python3 python3-pip
```

### 1.5 Python 설치 확인
```bash
python --version
# 또는
python3 --version

pip --version
# 또는
pip3 --version
```

## 2. Node.js 설치

### 2.1 Node.js 다운로드
1. [Node.js 공식 웹사이트](https://nodejs.org/) 방문
2. LTS(Long Term Support) 버전 다운로드 (권장)
3. 운영체제에 맞는 설치 파일 선택

### 2.2 Windows에서 Node.js 설치
```bash
# 설치 파일 실행 후 기본 설정으로 설치
# PATH 환경변수 자동 설정됨
```

### 2.3 macOS에서 Node.js 설치
```bash
# Homebrew 사용 (권장)
brew install node

# 또는 공식 설치 파일 사용
```

### 2.4 Linux에서 Node.js 설치
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# CentOS/RHEL
curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
sudo yum install -y nodejs
```

### 2.5 Node.js 설치 확인
```bash
node --version
npm --version
```

## 3. Git 설치

### 3.1 Windows에서 Git 설치
1. [Git for Windows](https://git-scm.com/download/win) 다운로드
2. 설치 파일 실행 후 기본 설정으로 설치

### 3.2 macOS에서 Git 설치
```bash
# Homebrew 사용
brew install git

# 또는 Xcode Command Line Tools 설치
xcode-select --install
```

### 3.3 Linux에서 Git 설치
```bash
# Ubuntu/Debian
sudo apt install git

# CentOS/RHEL
sudo yum install git
```

### 3.4 Git 설치 확인
```bash
git --version
```

## 4. Playwright 설치

### 4.1 Python용 Playwright 설치
```bash
# pip를 사용한 설치
pip install playwright

# 또는 특정 버전 설치
pip install playwright==1.40.0
```

### 4.2 Playwright 브라우저 설치
```bash
# 모든 브라우저 설치 (권장)
playwright install

# 특정 브라우저만 설치
playwright install chromium
playwright install firefox
playwright install webkit

# Chrome 브라우저만 설치 (프로젝트에서 사용)
playwright install chromium
```

### 4.3 설치 확인
```python
# Python에서 테스트
python -c "from playwright.sync_api import sync_playwright; print('Playwright 설치 성공!')"
```

## 5. 추가 Python 라이브러리 설치

### 5.1 프로젝트에 필요한 라이브러리들
```bash
# 데이터 처리
pip install pandas
pip install openpyxl

# HTML 파싱
pip install lxml

# HTTP 요청
pip install requests

# 기타 유틸리티
pip install asyncio
```

### 5.2 requirements.txt 사용 (권장)
```bash
# requirements.txt 파일 생성
echo "playwright>=1.40.0
pandas>=1.5.0
openpyxl>=3.0.0
lxml>=4.9.0
requests>=2.28.0" > requirements.txt

# 한 번에 설치
pip install -r requirements.txt
```

## 6. 가상환경 설정 (권장)

### 6.1 가상환경 생성
```bash
# 프로젝트 디렉토리로 이동
cd your_project_directory

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 6.2 가상환경에서 라이브러리 설치
```bash
# 가상환경이 활성화된 상태에서
pip install -r requirements.txt
```

## 7. Chrome 브라우저 설정

### 7.1 Chrome 설치 확인
```bash
# Windows에서 Chrome 설치 경로 확인
# 기본 경로: C:\Program Files\Google\Chrome\Application\chrome.exe
```

### 7.2 Chrome 경로 설정
```python
# smartThings_main.py에서 Chrome 경로 확인
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
```

## 8. 설치 검증

### 8.1 간단한 테스트 스크립트
```python
# test_playwright.py
from playwright.sync_api import sync_playwright

def test_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://www.google.com')
        print("Playwright 테스트 성공!")
        browser.close()

if __name__ == "__main__":
    test_playwright()
```

### 8.2 테스트 실행
```bash
python test_playwright.py
```

## 9. 문제 해결

### 9.1 일반적인 설치 문제

#### Python 경로 문제
```bash
# Windows에서 PATH 확인
echo %PATH%

# Python 경로 추가
set PATH=%PATH%;C:\Python311;C:\Python311\Scripts
```

#### pip 업그레이드
```bash
python -m pip install --upgrade pip
```

#### 권한 문제 (Linux/macOS)
```bash
# pip 설치 시 권한 문제 해결
pip install --user package_name

# 또는 sudo 사용 (권장하지 않음)
sudo pip install package_name
```

### 9.2 Playwright 관련 문제

#### 브라우저 설치 실패
```bash
# 캐시 정리 후 재설치
playwright install --force
```

#### 의존성 문제
```bash
# 시스템 의존성 설치 (Ubuntu/Debian)
sudo apt-get install -y libwoff1 libopus0 libwebp7 libwebpdemux2 libenchant1c2a libgudev-1.0-0 libsecret-1-0 libhyphen0 libgdk-pixbuf2.0-0 libegl1 libnotify4 libxslt1.1 libevent-2.1-7 libgles2 libvpx7
```

#### Windows 특정 문제
```bash
# Visual Studio Build Tools 설치
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

## 10. 환경 변수 설정

### 10.1 Windows 환경 변수
```bash
# 시스템 환경 변수에 추가
PYTHONPATH=C:\Python311;C:\Python311\Scripts
PATH=%PATH%;C:\Python311;C:\Python311\Scripts
```

### 10.2 macOS/Linux 환경 변수
```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export PYTHONPATH="/usr/local/bin/python3:/usr/local/bin"
export PATH="$PATH:/usr/local/bin"
```

## 11. IDE 설정

### 11.1 VS Code 설정
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true
}
```

### 11.2 PyCharm 설정
1. File → Settings → Project → Python Interpreter
2. 가상환경 경로 선택: `./venv/Scripts/python.exe`

## 12. 최종 확인 체크리스트

- [ ] Python 3.8+ 설치 및 PATH 설정
- [ ] Node.js LTS 설치 및 PATH 설정
- [ ] Git 설치 및 PATH 설정
- [ ] Playwright Python 패키지 설치
- [ ] Playwright 브라우저 설치
- [ ] 추가 Python 라이브러리 설치
- [ ] 가상환경 설정 (권장)
- [ ] Chrome 브라우저 경로 확인
- [ ] 테스트 스크립트 실행 성공
- [ ] IDE 설정 완료

## 13. 추가 리소스

### 13.1 공식 문서
- [Playwright Python Documentation](https://playwright.dev/python/)
- [Python 공식 문서](https://docs.python.org/)
- [Node.js 공식 문서](https://nodejs.org/docs/)

### 13.2 커뮤니티
- [Playwright GitHub](https://github.com/microsoft/playwright)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/playwright)
- [Playwright Discord](https://discord.gg/playwright)

## 14. 업데이트 및 유지보수

### 14.1 정기 업데이트
```bash
# Python 패키지 업데이트
pip list --outdated
pip install --upgrade package_name

# Playwright 업데이트
pip install --upgrade playwright
playwright install
```

### 14.2 버전 관리
```bash
# 현재 설치된 버전 확인
pip freeze > requirements.txt
```

이 가이드를 따라하면 Playwright를 사용하기 위한 모든 환경을 성공적으로 구축할 수 있습니다.
