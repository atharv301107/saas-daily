# SaaS Intelligence Daily Bot 🚀

An automated SaaS intelligence gathering and publishing system that reverse-engineers successful SaaS businesses, extracting actionable business models, growth strategies, and execution advice for founders, indie hackers, and developers.

It runs **daily** at zero infrastructure cost by utilizing Python, Google Gemini (free tier), JSON storage, GitHub Actions, and the Telegram Bot API.

---

## 📋 Core Objectives of the Daily Breakdown

Every day, the system publishes a report addressing the following dimensions of a successful SaaS:
1. **Core Pain Point**: The specific problem, who experienced it, its frequency/severity, and why it was painful.
2. **Old Solution**: How it was solved previously and why old methods failed.
3. **The SaaS Solution**: What was built, its core feature, supporting features, and unique advantages.
4. **Why Customers Paid**: Core benefits and measurable outcomes.
5. **Customer Profile**: Target customer segment and business size.
6. **Growth Engine**: Acquisition channels, primary growth levers, and growth loop.
7. **Revenue Model**: Business model, pricing logic, and upgrade path drivers.
8. **Moat**: Moat type, strength, and barrier to replication.
9. **Risks & Mistakes**: Historical execution mistakes and current market risks.
10. **Founder Lesson**: The single most stealable takeaway.
11. **India Opportunity**: Market transferability, local target segments, potential, and reasoning.
12. **Micro-SaaS Version**: Suggested MVP specs, features, target customers, and price points.

---

## 🛠 Project Structure

```
.github/
  workflows/
    daily_report.yml          # GitHub Actions daily scheduler (runs cron + git commit)
data/
  seed_companies.json         # Seed queue containing 35+ high-potential B2B / bootstrapped startups
  analyzed_companies.json     # flat-file JSON database containing history of analyzed companies
src/
  __init__.py
  config.py                   # Environment configuration loader (supports local .env files)
  db_manager.py               # JSON read/write operations and database management
  llm_client.py               # Gemini 1.5 Flash client for research and report generation
  telegram_client.py          # Formats and sends chunked HTML messages to Telegram
  main.py                     # Execution orchestrator
requirements.txt              # Project dependencies
README.md                     # Documentation
```

---

## 🚀 Setup & Deployment Guide

### Step 1: Create a Telegram Bot and Channel
1. Search for `@BotFather` on Telegram.
2. Send `/newbot` and follow instructions to name the bot and generate an API Token (`TELEGRAM_BOT_TOKEN`).
3. Create a **Telegram Channel** or **Telegram Group** where you want reports published.
4. Add your newly created bot to the Channel/Group as an **Administrator** with permission to post messages.
5. Retrieve your Chat ID (`TELEGRAM_CHAT_ID`):
   * For public channels, use your username (e.g. `@my_saas_channel`).
   * For private channels or groups, forward a message from your channel to `@ShowJsonBot` or `@username_to_id_bot` to get the numerical ID (which usually starts with `-100`).

### Step 2: Get a Free Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Log in with your Google account.
3. Click on **Create API Key** and copy your `GEMINI_API_KEY`.

### Step 3: Configure GitHub Repository Secrets
1. Push this codebase to your own GitHub repository.
2. In your repository, go to **Settings > Secrets and variables > Actions**.
3. Create three new **Repository Secrets**:
   * `TELEGRAM_BOT_TOKEN`: The token you got from BotFather.
   * `TELEGRAM_CHAT_ID`: The ID of your Telegram channel/group.
   * `GEMINI_API_KEY`: The API key you got from Google AI Studio.

### Step 4: Configure Repository Permissions for Git Push
1. In your GitHub repository, go to **Settings > Actions > General**.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Click **Save**. This allows the GitHub Actions run to commit updates to `data/analyzed_companies.json` back to your codebase.

---

## 🧪 Local Testing

To test the system on your local machine before pushing to GitHub:

1. Clone your repository.
2. Install Python 3.10+ and run:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_telegram_chat_id_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
4. Run the orchestrator:
   ```bash
   python -m src.main
   ```
   *Note: If no Telegram keys are provided, the script will output the entire report content directly to your terminal screen for verification.*

---

## 🛠 Maintenance & Customization

* **Adding Custom Startups**: You can add specific companies you want analyzed by appending them directly to the `data/seed_companies.json` file.
* **Managing History**: To reset the list of analyzed companies or allow the bot to re-analyze past startups, clear the array inside `data/analyzed_companies.json` (set it to `[]`).
* **Changing the Schedule**: The workflow is configured to run at `09:00 UTC` daily. You can adjust this schedule by changing the `cron` expression in `.github/workflows/daily_report.yml`.
