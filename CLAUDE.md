# CLAUDE.md - Navigation for Claude Code

**Last Updated**: 2024-10-31
**Session**: Context restoration after implementing AI-Assisted Maintenance System

---

## 🎯 Quick Start for Claude Code

This repository contains a **2-level AI-Assisted Maintenance System** designed to help non-technical users maintain code with AI assistance.

### For New Sessions: Read These First

1. **@README.md** - Project overview and quick start guide
2. **@L1-CLAUDE.md** - Full project context and AI workflow integration
3. **@.ai-maintenance/L0-WORKFLOW-MASTER.md** - 5-step maintenance workflow

---

## 📋 Recent Session Summary (2024-10-31)

### What Was Accomplished

**Created comprehensive AI-Assisted Maintenance documentation system:**

1. **L0 Meta Documents** (`.ai-maintenance/` folder):
   - L0-WORKFLOW-MASTER.md: 5-step workflow (Preparation → Complexity Analysis → Implementation → Testing → Review → Documentation)
   - L0-DOCUMENT-INDEX.md: Document finder and quick reference
   - L0-HANDOFF-CHECKLIST.md: Developer handoff guide (6-8 hours)
   - README.md: System overview and 2-level architecture

2. **L1 Project Documents** (project root):
   - L1-CLAUDE.md: AI context and project architecture (this is the main reference)
   - L1-COMPLEXITY-MATRIX.md: LOW/MEDIUM/HIGH classification criteria
   - L1-CONSTRAINTS.md: Absolute prohibitions and caution areas
   - L1-TESTING.md: Test procedures for all 6 sub-projects

3. **L2 Living Documents** (continuously updated):
   - L2-EXAMPLES.md: Success/failure case studies (7 initial examples)
   - L2-PROMPTS.md: 10 standardized AI prompt templates

4. **Supporting Files**:
   - QUICKSTART.md: Quick reference for all roles
   - README.md: Updated with project overview and system guide
   - .gitignore: Added to exclude large files (208MB Excel files)

### Git Operations

```bash
# Two remote repositories configured:
origin: https://github.com/TaebeomHeo/WWAI-03-SOP.git
ww-git: https://git.swclick.com/bombbie/WWAI-SOP-v0.9.git

# Latest commits:
fe3262b - Remove large CGD Excel files (208MB) and add .gitignore
196c424 - Add comprehensive AI-Assisted Maintenance System
5944eab - Create README.md
```

### Repository Description (for GitHub)

```
AI-Assisted Code Maintenance System: 2-level documentation framework enabling non-technical users to maintain Samsung web automation projects with AI tools (Claude, ChatGPT, Cursor)
```

---

## 🏗️ Project Structure Overview

```
WWAI-03-SOP/
│
├── 📂 .ai-maintenance/              L0: Universal guidelines
│   ├── L0-WORKFLOW-MASTER.md       ⭐⭐⭐ 5-step workflow (most important)
│   ├── L0-DOCUMENT-INDEX.md        Document finder
│   ├── L0-HANDOFF-CHECKLIST.md     Developer handoff guide
│   └── README.md                   System overview
│
├── 📄 L1-CLAUDE.md                  ⭐⭐⭐ Main AI context (read this!)
├── 📄 L1-COMPLEXITY-MATRIX.md       Complexity classification
├── 📄 L1-CONSTRAINTS.md             Critical constraints
├── 📄 L1-TESTING.md                 Test procedures
│
├── 📄 L2-EXAMPLES.md                Case studies (growing)
├── 📄 L2-PROMPTS.md                 AI prompt templates
│
├── 📄 README.md                     Project overview
├── 📄 QUICKSTART.md                 Quick reference
├── 📄 CLAUDE.md                     This file (navigation)
│
├── 📂 01.smartThings/               SmartThings automation framework
│   ├── smartThings_main.py
│   └── smartThings_module/
│
└── 📂 02.ENH/                       Enhanced web validation tools
    ├── gnb/                         GNB/CGD menu validation
    ├── pd/                          Product page validation
    ├── pf/                          Product Finder validation
    ├── shop/                        SHOP navigation extraction
    └── smartthings-logic/           AI story recommendation
```

---

## 🤖 How to Use This System (for AI)

### When Working on This Repository

**Always provide these files to understand context:**

1. **For any task**: Start with `@L1-CLAUDE.md`
2. **For complexity evaluation**: Add `@L1-COMPLEXITY-MATRIX.md` + `@L1-CONSTRAINTS.md`
3. **For implementation**: Add `@L2-EXAMPLES.md` + `@{target_file}`
4. **For testing**: Add `@L1-TESTING.md`

### Complexity Classification

- 🟢 **LOW**: Configuration changes, strings, data files (15-30 min)
- 🟡 **MEDIUM**: New validation rules, CSS selectors, logic branches (1-2 hours + review)
- 🔴 **HIGH**: async/await, Playwright flows, core algorithms (developer required)

### Critical Constraints (NEVER modify without approval)

1. async/await patterns
2. Python version (must stay 3.11.9)
3. Core dependencies in requirements.txt
4. Playwright browser launch configurations
5. API response monitoring logic (01.smartThings)
6. 5-stage recommendation logic (smartthings-logic)

---

## 📦 Main Projects

### 01.smartThings - SmartThings Automation Framework

**Purpose**: Automated testing of Samsung SmartThings web pages across multiple countries (DE, FR, ES, IT)

**Key Tech**: Playwright (async), Pandas, Excel data processing

**Run**: `python 01.smartThings/smartThings_main.py`

**Architecture**:
1. Load test data from Excel
2. Launch browser and navigate
3. Monitor 4 API endpoints
4. Extract HTML after template binding
5. Compare expected vs actual results

### 02.ENH - Enhanced Web Validation Tools

**5 sub-projects**:
- **gnb**: GNB/CGD menu structure validation
- **pd**: Product page validation (5 checks: rating, cart, links, dimension, price)
- **pf**: Product Finder validation (11 checks)
- **shop**: SHOP navigation extraction
- **smartthings-logic**: AI-powered story recommendation (OpenAI API)

**Common setup**:
```bash
cd 02.ENH/{project}
python -m venv .venv
source .venv/bin/activate  # macOS
pip install -r requirements.txt
python main.py
```

---

## 🔑 Key Files to Reference

| Task | Files to Provide |
|------|------------------|
| **Understand project** | @L1-CLAUDE.md + @README.md |
| **Complexity analysis** | @L1-CLAUDE.md + @L1-COMPLEXITY-MATRIX.md + @L1-CONSTRAINTS.md |
| **Implementation** | @L1-CLAUDE.md + @L2-EXAMPLES.md + @{target_file} |
| **Code review** | @L1-CONSTRAINTS.md + @{modified_file} |
| **Testing** | @L1-TESTING.md |
| **Error debugging** | @L1-CLAUDE.md + @L2-EXAMPLES.md + error message |

---

## 📊 System Status

**Documentation System**: ✅ Complete (v1.0)
- L0 Meta Documents: 4 files
- L1 Project Documents: 4 files
- L2 Living Documents: 2 files (will grow with use)

**Git Repositories**: ✅ Synchronized
- GitHub (origin): Up to date
- ww-git (internal): Up to date

**Large Files**: ⚠️ Excluded
- 02.ENH/gnb/cgddocs/ (208MB Excel files) excluded via .gitignore
- Files remain locally, not tracked in Git

---

## 🚀 Next Session: Where to Continue

### For Code Maintenance Tasks

1. **Start**: Read request → Classify complexity using L1-COMPLEXITY-MATRIX.md
2. **Implement**: Follow L0-WORKFLOW-MASTER.md steps
3. **Document**: Update L2-EXAMPLES.md with results

### For New Features

1. **Understand**: @L1-CLAUDE.md for architecture
2. **Plan**: Identify affected modules
3. **Implement**: Follow coding patterns in existing code
4. **Test**: Use L1-TESTING.md procedures

### For System Evolution

- Update L2-EXAMPLES.md with new case studies
- Refine L2-PROMPTS.md based on usage
- Maintain L1-CONSTRAINTS.md as new issues discovered

---

## 📝 Important Notes

1. **This is L1-CLAUDE.md's companion**: This file (CLAUDE.md) is for quick navigation. For full context, always read L1-CLAUDE.md.

2. **Living system**: L2 documents grow with use. After completing tasks, update L2-EXAMPLES.md.

3. **Safety first**: Always check L1-CONSTRAINTS.md before modifying code.

4. **AI workflow**: Use standardized prompts from L2-PROMPTS.md for consistency.

5. **Large files**: cgddocs/ folder (208MB) is .gitignored but exists locally.

---

## 🔗 External Resources

- **Claude Code**: https://claude.ai/code
- **GitHub Repo**: https://github.com/TaebeomHeo/WWAI-03-SOP
- **Internal Git**: https://git.swclick.com/bombbie/WWAI-SOP-v0.9

---

**For detailed information, always start with**: `@L1-CLAUDE.md`

**Version**: 1.0
**Last Session**: 2024-10-31
**Next Review**: As needed based on usage
