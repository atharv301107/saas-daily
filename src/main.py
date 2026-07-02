import sys
from datetime import datetime
import src.config as config
import src.db_manager as db
import src.llm_client as llm
import src.telegram_client as telegram

# Force stdout/stderr to UTF-8 to prevent encoding crashes with emojis on Windows/CI
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    print(f"[{datetime.utcnow().isoformat()}] Starting SaaS Intelligence Daily Run...")
    
    # 1. Validate environment configurations
    config.validate_config()
    
    # 2. Load databases
    analyzed_list = db.load_analyzed_companies()
    seed_list = db.load_seed_companies()
    
    print(f"[INFO] Loaded {len(seed_list)} seed companies and {len(analyzed_list)} already analyzed companies.")
    
    # Normalize helper for comparisons
    def normalize(val):
        return str(val).strip().lower().replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
    
    analyzed_names = {normalize(c.get("name", "")) for c in analyzed_list}
    analyzed_urls = {normalize(c.get("website", "")) for c in analyzed_list if c.get("website")}
    
    selected_company = None
    
    # 3. Select next company
    # Try seed list first
    for seed in seed_list:
        name = seed.get("name", "")
        url = seed.get("website", "")
        if normalize(name) not in analyzed_names and (not url or normalize(url) not in analyzed_urls):
            selected_company = seed
            print(f"[INFO] Selected '{name}' from the seed queue.")
            break
            
    # If seed queue is exhausted, ask Gemini
    if not selected_company:
        print("[INFO] Seed queue is exhausted. Asking Gemini to recommend a new SaaS company...")
        try:
            selected_company = llm.suggest_new_company(analyzed_list)
            # Double-check against our database list
            name = selected_company.get("name", "")
            url = selected_company.get("website", "")
            if normalize(name) in analyzed_names or (url and normalize(url) in analyzed_urls):
                print(f"[WARNING] Gemini suggested '{name}' ({url}) which is already analyzed. Attempting secondary suggestion...")
                # Let it try once more
                selected_company = llm.suggest_new_company(analyzed_list)
            print(f"[INFO] Gemini suggested unique company: '{name}' ({url})")
        except Exception as e:
            print(f"[ERROR] Failed to get dynamic suggestion from Gemini: {e}")
            print("[INFO] Falling back to re-analyzing the first seed company as a safety measure.")
            if seed_list:
                selected_company = seed_list[0]
            else:
                print("[CRITICAL] No seed companies available and LLM suggestion failed. Exiting.")
                sys.exit(1)
                
    # 4. Generate Report
    report_num = len(analyzed_list) + 1
    print(f"[INFO] Generating report #{report_num} for '{selected_company.get('name')}'...")
    
    try:
        report_text = llm.generate_report(selected_company, report_num)
        print("[INFO] SaaS Report generated successfully.")
    except Exception as e:
        print(f"[ERROR] Gemini report generation failed: {e}")
        sys.exit(1)
        
    # 5. Extract score
    score = llm.extract_opportunity_score(report_text)
    print(f"[INFO] Extracted Overall Opportunity Score: {score}/10")
    
    # 6. Publish to Telegram
    telegram.send_telegram_report(report_text)
    
    # 7. Update database of analyzed companies
    db.mark_company_analyzed(
        name=selected_company.get("name"),
        website=selected_company.get("website"),
        category=selected_company.get("category", "Uncategorized"),
        score=score
    )
    
    print(f"[{datetime.utcnow().isoformat()}] Run completed successfully.")

if __name__ == "__main__":
    main()
