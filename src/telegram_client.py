import requests
import src.config as config

def send_telegram_report(text: str):
    """
    Sends the generated SaaS Intelligence Report to the configured Telegram chat/channel.
    Splits the message into chunks if it exceeds Telegram's 4096 character limit.
    """
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("[WARNING] Telegram credentials (TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID) are missing.")
        print("[INFO] Outputting the generated report to console/stdout instead:\n")
        print(text)
        return
        
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Split text into chunks to respect Telegram's limit (leaving some margin for formatting tags)
    max_chunk_size = 4000
    chunks = []
    
    current_chunk = ""
    for line in text.split("\n"):
        # If adding the next line exceeds limits, store current chunk and start a new one
        if len(current_chunk) + len(line) + 1 > max_chunk_size:
            chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    for idx, chunk in enumerate(chunks):
        payload = {
            "chat_id": config.TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        try:
            print(f"[INFO] Sending report chunk {idx+1}/{len(chunks)} to Telegram...")
            response = requests.post(url, json=payload, timeout=20)
            
            if response.status_code == 200:
                print(f"[INFO] Report chunk {idx+1} delivered successfully.")
            else:
                print(f"[ERROR] Failed to send Telegram message: {response.status_code} - {response.text}")
                # Fallback to plain text if HTML parsing failed (usually due to unclosed tags or characters like '<' or '>')
                if "can't parse entities" in response.text or "bad request" in response.text.lower():
                    print("[WARNING] HTML parsing failed. Retrying in plain text mode...")
                    payload.pop("parse_mode", None)
                    fallback_response = requests.post(url, json=payload, timeout=20)
                    if fallback_response.status_code == 200:
                        print("[INFO] Deliver successful in plain text fallback mode.")
                    else:
                        print(f"[ERROR] Fallback plain text delivery failed: {fallback_response.status_code} - {fallback_response.text}")
        except Exception as e:
            print(f"[ERROR] Connection error while calling Telegram API: {e}")
