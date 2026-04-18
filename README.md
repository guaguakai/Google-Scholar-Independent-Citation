# Google Scholar Citation Parser for RFE Evidence

An automated tool for academics responding to USCIS Green Card RFEs (Request for Evidence). This script crawls your Google Scholar profile, parses every paper that cites you, identifies **independent citations**, highlights them in yellow, and merges the results into organized PDFs.

## Features
- **Auto-Highlighting**: Identifies independent citations by checking for author overlap.
- **RFE Ready**: Prints PDFs with headers/footers (URL and date) as required by USCIS.
- **Captcha Handling**: Pauses execution and waits for human verification if Google blocks traffic.
- **Consolidation**: Merges multi-page citation records into a single PDF per publication.
- **Statistics**: Provides a total count of independent vs. dependent citations.

## Setup
1. Install requirements:
   `pip install -r requirements.txt`
2. Set your Google Scholar ID in `main.py` or as an environment variable.
3. Add your name and collaborators to the `EXCLUSION_LIST`.

## License
MIT License - See LICENSE file for details.
