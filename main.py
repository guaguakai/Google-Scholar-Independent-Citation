import time
import os
import base64
import re
import fitz  # PyMuPDF
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
# Use an environment variable or manually input Scholar ID
SCHOLAR_ID = os.getenv("SCHOLAR_ID", "YOUR_SCHOLAR_ID_HERE") 
OUTPUT_DIR = os.path.abspath("Scholar_Citation_Evidence")

# Add your name variants and known frequent co-authors here
# This is critical for accurate "Independence" checking
EXCLUSION_LIST = ["Your Name", "Y. Name", "Common Co-Author"]

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def check_for_captcha(driver):
    captcha_keywords = ["unusual traffic", "not a robot", "captcha", "prove you are human"]
    while any(word in driver.page_source.lower() for word in captcha_keywords):
        print("\n[!] VERIFICATION REQUIRED: Please solve the CAPTCHA in the browser window.")
        time.sleep(5)

def parse_authors(author_string):
    clean_str = author_string.split("-")[0] 
    return [n.strip().replace("...", "").replace("…", "") for n in clean_str.split(",")]

def highlight_page(driver, original_authors, citing_papers):
    print_options = {'displayHeaderFooter': True, 'printBackground': True, 'preferCSSPageSize': True}
    result = driver.execute_cdp_cmd("Page.printToPDF", print_options)
    
    raw_pdf_bytes = base64.b64decode(result['data'])
    doc = fitz.open(stream=raw_pdf_bytes, filetype="pdf")
    all_excl_names = [n.lower() for n in (original_authors + EXCLUSION_LIST)]
    
    page_ind, page_dep = 0, 0

    for citing_paper in citing_papers:
        citing_authors = [a.lower() for a in citing_paper['authors']]
        is_independent = not any(name in all_excl_names for name in citing_authors)
        
        if is_independent:
            page_ind += 1
            raw_title = citing_paper['title']
            clean_title = re.sub(r'^\[[A-Z]+\]\s*', '', raw_title, flags=re.IGNORECASE).strip()
            
            words = clean_title.split()
            search_variants = [" ".join(words[:8]), " ".join(words[:5]), " ".join(words[:3])]
            
            found = False
            for page in doc:
                for query in search_variants:
                    if not query or len(query) < 5: continue
                    text_instances = page.search_for(query)
                    if text_instances:
                        for inst in text_instances:
                            annot = page.add_highlight_annot(inst)
                            annot.set_colors(stroke=(1, 1, 0)) # Yellow
                            annot.update()
                            page.insert_text((inst.x0, inst.y0 - 2), "INDEPENDENT", color=(1, 0, 0), fontsize=6)
                        found = True
                        break
                if found: break
        else:
            page_dep += 1

    return doc.tobytes(), page_ind, page_dep

def main():
    driver = get_driver()
    total_ind, total_dep = 0, 0
    
    try:
        driver.get(f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en")
        check_for_captcha(driver)
        
        while True: # Expand publications
            try:
                more_btn = driver.find_element(By.ID, "gsc_bpf_more")
                if more_btn.is_enabled(): more_btn.click(); time.sleep(2)
                else: break
            except: break

        rows = driver.find_elements(By.CLASS_NAME, "gsc_a_tr")
        papers = []
        for row in rows:
            title = row.find_element(By.CLASS_NAME, "gsc_a_at").text
            auths = parse_authors(row.find_element(By.CLASS_NAME, "gs_gray").text)
            try:
                link = row.find_element(By.CLASS_NAME, "gsc_a_ac").get_attribute("href")
                if link: papers.append({"title": title, "authors": auths, "url": link})
            except: continue

        for paper in papers:
            driver.get(paper["url"])
            page_num = 1
            paper_clean_name = "".join(x for x in paper["title"][:35] if x.isalnum() or x==" ").strip()
            paper_ind, paper_dep = 0, 0
            paper_merger = fitz.open()

            while True:
                time.sleep(4)
                check_for_captcha(driver)
                citing_results = []
                for ri in driver.find_elements(By.CLASS_NAME, "gs_ri"):
                    try:
                        t = ri.find_element(By.CLASS_NAME, "gs_rt").text
                        a = parse_authors(ri.find_element(By.CLASS_NAME, "gs_a").text)
                        citing_results.append({"title": t, "authors": a})
                    except: continue

                page_data, p_ind, p_dep = highlight_page(driver, paper["authors"], citing_results)
                paper_ind += p_ind; paper_dep += p_dep
                
                page_doc = fitz.open(stream=page_data, filetype="pdf")
                paper_merger.insert_pdf(page_doc)
                page_doc.close()

                try:
                    next_btn = driver.find_elements(By.XPATH, '//div[@id="gs_n"]//a[contains(., "Next")]')
                    if next_btn and next_btn[0].is_displayed():
                        next_btn[0].click(); page_num += 1
                    else: break
                except: break

            if page_num > 0:
                final_path = os.path.join(OUTPUT_DIR, f"{paper_clean_name}_Citations.pdf")
                paper_merger.save(final_path)
                total_ind += paper_ind; total_dep += paper_dep
            paper_merger.close()

        print(f"\nFinal Totals -> Independent: {total_ind} | Dependent: {total_dep}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
