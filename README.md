# ♟️ Chess.com Weekly Summary Bot

This bot automatically fetches Chess.com stats for specified users, generates a weekly image summary, and sends it to a Discord channel using a webhook.

## 📦 Features
- Pulls past 7 days of games
- Calculates rating, wins/losses
- Highlights top performer
- Sends to Discord with image

## 🛠 Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Replace `WEBHOOK_URL` in `weekly_chess_summary.py` with your Discord webhook.

3. Run manually:
   ```bash
   python weekly_chess_summary.py
   ```

## 🔁 Automate with Cron (Linux)

1. Open your crontab:
   ```bash
   crontab -e
   ```

2. Add this line to run every Sunday at 10 AM:
   ```bash
   0 10 * * SUN /usr/bin/python3 /full/path/to/weekly_chess_summary.py
   ```

Make sure to use the full path to your Python interpreter and script file.

## 🧑‍💻 Dependencies
- [Chess.com API](https://www.chess.com/news/view/published-data-api)
- Pillow (for image generation)
- Discord Webhook API
