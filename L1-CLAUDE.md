# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains Samsung web automation and testing tools, organized into two main sections:
1. **01.smartThings/**: Original SmartThings automation test framework (Korean documentation)
2. **02.ENH/**: Enhanced web validation tools for Samsung global websites

## Project Structure

```
WWAI-03-SOP/
├── 01.smartThings/           # SmartThings automation testing
│   ├── smartThings_main.py   # Main execution file
│   ├── smartThings_module/   # Core modules
│   └── ReadMe/               # Korean documentation
│
├── 02.ENH/                   # Enhanced web validation tools
│   ├── gnb/                  # GNB/CGD menu validation
│   ├── pd/                   # Product page validation
│   ├── pf/                   # Product Finder validation
│   ├── shop/                 # SHOP navigation extraction
│   └── smartthings-logic/    # AI-powered story recommendation
```

## 01.smartThings - SmartThings Automation Framework

### Purpose
Automated testing of Samsung SmartThings web pages across multiple accounts and countries (DE, FR, ES, IT).

### Key Technologies
- **Playwright**: Browser automation
- **Pandas**: Excel data processing
- **asyncio**: Asynchronous execution

### Running Tests
```bash
python 01.smartThings/smartThings_main.py
```

### Architecture
The system follows this workflow:
1. Load test data from Excel (`RowDataExcel`)
2. Launch browser and navigate to SmartThings pages
3. Monitor 4 API endpoints (story, product, meta, consent)
4. Extract HTML data after template binding completes
5. Compare expected vs actual results
6. Save results to Excel with screenshots

### Critical Components
- **smartThings_module/rowdata_excel.py**: Excel data processing, country-specific data copying
- **smartThings_module/response_handler.py**: API response monitoring (AccountDataCollector class)
- **smartThings_module/html_result.py**: HTML data extraction (HtmlExtractor class)
- **smartThings_module/compare_result.py**: Result comparison (CompareProcess class)
- **smartThings_module/product_result.py**: Product priority calculation
- **smartThings_module/law_agree_result.py**: Legal consent requirement handling

### Important Notes
- Requires Chrome browser installation
- Uses hardcoded Windows file paths (needs adjustment for macOS)
- Login credentials: qauser/qauser1!
- API timeout: 60 seconds
- HTML binding wait: 80 seconds with `{{` pattern detection
- Retry logic: 3 attempts per account

## 02.ENH - Enhanced Web Validation Tools

All tools in this section share common patterns:
- Python 3.11.9 required
- Virtual environment setup: `python -m venv .venv`
- Activate: `.venv/Scripts/activate` (Windows) or `source .venv/bin/activate` (macOS)
- Install dependencies: `pip install -r requirements.txt`

### gnb - GNB/CGD Menu Validation

**Purpose**: Validate menu structure and links against CGD Excel documentation.

**Running**:
```bash
cd 02.ENH/gnb
python cgd.py        # First: convert Excel to JSON
python main.py       # Then: run validation
```

**Key Features**:
- Extracts GNB menu structure from web pages
- Compares with CGD Excel data (menu names, URLs)
- Validates all menu links (HTTP 200, error page detection)
- Results saved to `crawlstore/` as JSON

**Important Files**:
- `cgd.py`: Excel to JSON converter (run first)
- `gnb.py`: GNB extraction logic
- `verify.py`: Link validation
- `main.py`: Main orchestration
- Place CGD Excel files in `cgddocs/` folder

### pd - Product Page Validation

**Purpose**: Validate product page functionality (cart, dimension, links, prices).

**Running**:
```bash
cd 02.ENH/pd
python main.py              # Local testing
python main.py --ssi 1234   # PlateAPI integration
```

**Test Coverage**:
1. **Rating validation**: Check if ratings exist on page
2. **Cart transition**: Verify "Add to Cart" → Cart page flow (Standard/Simple PD)
3. **Broken link check**: Test all links in buying tool area
4. **Dimension check**: Test fit/not-fit functionality with random values
5. **Price matching**: Compare PD page price vs Cart page price

**Important Modules**:
- `pd_modules/navigation.py`: Page navigation
- `pd_modules/dimension.py`: Dimension testing
- `pd_modules/price.py`: Price comparison
- `pd_modules/links.py`: Link validation
- Results saved to `result/` as JSON

**WDS Login Configuration** (env.user):
- `WDS_LOGIN`: true/false (use SSO login)
- `WDS_USERNAME`, `WDS_PASSWORD`: Internal Samsung credentials
- `WDS_EMPLOYEE_MODE`: true (Employee)/false (Business Partner)

### pf - Product Finder Validation

**Purpose**: Comprehensive PF page structure and functionality validation.

**Running**:
```bash
cd 02.ENH/pf
python main.py              # Local testing
python main.py --ssi 1234   # Zest API integration
```

**Test Coverage** (11 validations):
1. **Broken Link**: nv19/nv20 menu URLs (HTTP 200, error page detection)
2. **Navigation Visible**: nv19/nv20 element visibility
3. **nv17 BreadCrumb**: Should not be visible on PF pages
4. **Headline**: Text block headline existence
5. **Result Count**: Displayed count ≥ actual product cards
6. **Sort**: Sort button text matches default and selected option
7. **Purchase**: All products have "buy" CTA
8. **Filter**: Filter application, text matching, purchase validation
9. **BreadCrumb**: Test vs Live environment consistency
10. **FAQ**: Test vs Live DOM structure comparison
11. **Disclaimer**: Test vs Live DOM structure comparison

**Important Modules**:
- `pf_modules/navigation.py`: nv19/nv20 navigation
- `pf_modules/filter.py`: Filter testing
- `pf_modules/comparison.py`: Test vs Live comparison
- Results saved to `crawlstore/` as JSON

**Filter Testing Strategy**:
- Individual tests: All checkboxes from filter index=1
- Random combinations: Max 3 combinations from other filters

### shop - SHOP Navigation Extraction

**Purpose**: Extract and validate SHOP menu structure (L0/L1/Product hierarchy).

**Running**:
```bash
cd 02.ENH/shop
python main.py
```

**Extraction Process**:
1. Extract L0 (main menu) buttons
2. Click each L0 → Extract L1 (sub menu) buttons
3. Click each L1 → Extract Product list
4. Validate all links (HTTP 200 check)
5. Save hierarchical tree to `crawlstore/` as JSON

**Important Files**:
- `shop.py`: SHOP structure extraction logic
- `json2excel.py`: JSON to Excel converter
- `main.py`: Main orchestration

### smartthings-logic - AI Story Recommendation

**Purpose**: LLM-powered story recommendation based on user interests and owned products.

**Running**:
```bash
cd 02.ENH/smartthings-logic
cp env.user.sample env.user   # Configure OpenAI API key
python main.py                # Batch processing
```

**Setup Requirements**:
- OpenAI API key in `env.user`
- Input files: `data/account.csv`, `data/story.csv`
- Prompt templates: `prompt/story_prompt.md`, `prompt/product_prompt.md`

**Recommendation Logic** (5-stage):
1. **Stage 1**: Match interest keywords exactly
2. **Stage 2**: Calculate product match counts
3. **Stage 3**: Apply 5-tier sorting (match count, story count, priority, mismatch count, mismatch priority)
4. **Stage 4**: Select top 2 stories (including ties)
5. **Stage 5**: Format results (special patterns, rankings)

**Special Cases**:
- "Ease of use + Mobile,TV" → "35-1, 35-3, 42-3, 35-2 중 랜덤"
- No interests/products → "38-2, 38-1"

**Alternative Usage - Chat Mode**:
```
Context files: @data/account.csv @data/story.csv @prompt/story_prompt_chat.md
Query: "계정 st_story1@teml.net에 맞는 스토리를 추천해주세요."
Note: Process 4 accounts at a time to avoid chat interruptions
```

**Output Files** (in `output/`):
- `story_reasoning_*.md`: Story recommendation analysis
- `product_reasoning_*.md`: Product recommendation analysis
- `final_results_*.xlsx`: Consolidated Excel report

**Maintenance**:
- To update logic: Edit `prompt/*.md` files (preferred)
- To change conditions: Edit `prompts.py` → `build_story_prompt()` function

## Common Development Patterns

### Environment Configuration
All 02.ENH projects use `env.user` for configuration:
- Copy from `env.user.template` or `env.user.sample`
- Contains API keys, file paths, login credentials
- Never commit `env.user` to version control

### Virtual Environment Setup
```bash
# Create
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Logging
Projects use `utility/orangelogger.py` for structured logging:
- Logs saved to `logs/` directory
- Filename format: `{MMDD}-{HHMMSS}.log`

### Result Files
- **01.smartThings**: Excel files with screenshots
- **02.ENH/gnb, shop, pf**: JSON files in `crawlstore/`
- **02.ENH/pd**: JSON files in `result/`
- **02.ENH/smartthings-logic**: Markdown + Excel in `output/`

### Playwright Browser Automation
Common patterns across projects:
- Chrome browser with custom user agent
- Headless mode configurable
- Cookie consent and modal handling
- Retry logic for stability
- Screenshot capture for debugging

## Testing Philosophy

### Link Validation
- HTTP 200 required
- Detect error pages even with 200 status (`.ot02-error-page` class)
- Handle redirects properly

### Test vs Live Comparison
- PF validates BreadCrumb, FAQ, Disclaimer against live site
- Ensures test environment matches production

### Accessibility and Visibility
- Elements must be visible (not just present in DOM)
- Use `is_visible()` checks before assertions

## Important File Path Patterns

### Windows-specific paths in 01.smartThings
```python
samsung_project_path = r'C:\Users\WW\Desktop\삼성 프로젝트 관련 파일'
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
```
These need adjustment when running on macOS.

### Data File Locations
- **01.smartThings**: Windows absolute paths
- **02.ENH**: Relative paths from project root (`data/`, `prompt/`, `output/`)

## Language Notes
- **01.smartThings**: Korean comments and documentation
- **02.ENH**: Mixed Korean/English (README in Korean, code mostly English)
- Variable names use descriptive English where possible

---

## AI-Assisted Maintenance System

This repository includes a comprehensive **AI-Assisted Maintenance System** that enables non-technical users to maintain this codebase with AI assistance.

### System Architecture

The documentation follows a **2-Level + Living Documents** structure:

**L0: Meta Documents** (`.ai-maintenance/` folder)
- Universal guidelines applicable to any project
- Rarely change, portable across projects
- Key file: **L0-WORKFLOW-MASTER.md** (5-step workflow)

**L1: Project Documents** (project root, this file included)
- Customized for this specific project
- Updated occasionally as project evolves
- Files: L1-CLAUDE.md (this file), L1-COMPLEXITY-MATRIX.md, L1-CONSTRAINTS.md, L1-TESTING.md

**L2: Living Documents** (project root)
- Continuously updated with case studies and learnings
- Files: L2-EXAMPLES.md, L2-PROMPTS.md

### When to Use This File

**Provide this file (@L1-CLAUDE.md) to AI when:**
1. **Step 1: Complexity Analysis** - Always include for context
2. **Step 2: Implementation** - Required for understanding project structure
3. **Error Debugging** - Helps AI understand the codebase architecture

**Combine with these files:**
- Complexity evaluation: + @L1-COMPLEXITY-MATRIX.md + @L1-CONSTRAINTS.md
- Implementation: + @L2-EXAMPLES.md + @{target_file}
- Code review: + @L1-CONSTRAINTS.md
- Testing: + @L1-TESTING.md

### Complexity Guidelines for This Project

**🟢 LOW Complexity** (non-technical users can handle alone):
- Configuration value changes (timeouts, retry counts, URLs)
- String modifications (messages, labels, file names)
- Data file updates (Excel, CSV, JSON data)
- Simple conditional threshold changes

**🟡 MEDIUM Complexity** (AI assistance + developer review required):
- Adding new validation rules
- Modifying CSS selectors
- Adding new conditional logic branches
- Changing data processing flow

**🔴 HIGH Complexity** (developer required):
- async/await pattern modifications
- Playwright automation flow changes
- Core algorithm modifications (priority calculation, sorting logic)
- New API endpoint integration
- Python version or dependency changes

### Critical Constraints

**NEVER modify these areas without developer approval:**
1. **async/await patterns** - Breaking these breaks the entire automation
2. **Python version** (must stay 3.11.9) - Dependency compatibility issues
3. **Core dependencies** in requirements.txt
4. **Playwright browser launch** configurations
5. **API response monitoring logic** in 01.smartThings
6. **5-stage recommendation logic** in smartthings-logic

**Exercise extreme caution with:**
- CSS selectors (website changes can break them)
- File path handling (Windows vs macOS differences)
- Conditional logic with multiple branches
- Data type conversions (str ↔ int ↔ float)

### AI Workflow Integration

When working with AI tools (Claude, ChatGPT, Cursor):

1. **Always start with Step 1** (Complexity Analysis)
   - Prevents overconfident changes
   - Routes to appropriate skill level

2. **Use standardized prompts** from L2-PROMPTS.md
   - Ensures consistent AI responses
   - Includes necessary context files

3. **Document all changes** in L2-EXAMPLES.md
   - Builds institutional knowledge
   - Helps future maintainers

4. **Test incrementally** following L1-TESTING.md
   - Catch issues early
   - Easier rollback if needed

### Quick Reference for AI

**Project Type**: Web automation & validation (Playwright + Python)
**Primary Language**: Python 3.11.9
**Main Frameworks**: Playwright (async), Pandas, OpenAI API
**Target Platform**: Samsung global websites
**Test Approach**: Comparison-based (expected vs actual)
**Logging**: OrangeLogger utility, logs in `logs/` folders
**Results**: JSON (crawlstore/, result/), Excel, Markdown

**Common Commands**:
```bash
# 01.smartThings
python 01.smartThings/smartThings_main.py

# 02.ENH projects (after activating .venv)
cd 02.ENH/{project_name}
python main.py              # Local testing
python main.py --ssi 1234   # API integration
```

**Key Patterns to Recognize**:
- **Browser automation**: All projects use Playwright with Chrome
- **Retry logic**: 3 attempts with timeout handling
- **Result comparison**: Expected vs Actual pattern
- **Logging**: Timestamp-based log files
- **Config files**: env.user for credentials and paths

---

**This file version**: 2.0
**Last updated**: 2024-10-31
**Maintenance system version**: 1.0
