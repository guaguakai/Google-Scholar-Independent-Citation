# Google Scholar Citation Parser for RFE Evidence

An automated tool designed for academics responding to **USCIS Green Card RFEs** (Request for Evidence). This script crawls a Google Scholar profile, parses citing papers, identifies **independent citations**, highlights them in yellow, and merges the results into organized, high-quality PDFs.

## Features
- **Independent Citation Detection**: Automatically cross-references citing authors against your original co-authors to distinguish independent work from self-citations or collaborator work.
- **Robust Highlighting**: Employs fuzzy word-matching and tag-stripping to ensure titles are highlighted in PDFs even when they contain tags like `[HTML]` or span multiple lines.
- **RFE Compliant**: Generates PDFs with mandatory headers and footers, including the source URL and access timestamp.
- **Auto-Merging**: Automatically consolidates multi-page citation records into a single merged PDF per publication for easier filing.
- **Smart Pause**: Detects Google "Unusual Traffic" blocks and pauses execution, allowing you to solve the CAPTCHA in the browser before automatically resuming.
- **Citation Statistics**: Provides a final tally of independent versus dependent citations for your profile and individual papers.

---

## Setup Instructions

### 1. Identify your Google Scholar ID
The `SCHOLAR_ID` is the unique 12-character alphanumeric string found in your profile URL.
* **Profile URL Example**: `https://scholar.google.com/citations?user=spWVns8AAAAJ&hl=en`
* **Your ID**: `spWVns8AAAAJ`

### 2. Set Environment Variables (Recommended)
To keep your script private and avoid hard-coding your ID into the codebase, set it as an environment variable in your terminal.

**On macOS / Linux (Terminal):**
```
export SCHOLAR_ID="your_id_here"
```

### 3. Installation
```
pip install selenium webdriver-manager pymupdf
```

### Configuration

If you prefer not to use environment variables, you can manually update the configuration block at the top of main.py:

* SCHOLAR_ID: Paste your 12-character ID.
* EXCLUSION_LIST: Add your name variants (e.g., "J. Doe", "John Doe") and the names of frequent collaborators to ensure the "Independent" count is accurate.

### Usage

Run the script from your terminal:

```
python main.py
```

Note: The script opens a visible Chrome window. If Google presents a "Prove you are human" check, solve it manually in that window. The script will detect the results page and resume automatically once the challenge is cleared.


### Output

All results are saved to a folder named Scholar_Citation_Evidence.

* File Format: [Paper_Title]_Citations.pdf
* Content: A single merged document for each paper where every independent citation is highlighted in yellow and marked with an "INDEPENDENT" label.

### License
MIT License
