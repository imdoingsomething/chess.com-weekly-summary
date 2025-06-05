### weekly_chess_summary.py

import requests
import datetime
from PIL import Image, ImageDraw, ImageFont
from discord_webhook import DiscordWebhook, DiscordEmbed

# CONFIGURATION
USERS = ["WizardinOzz", "nwicksman"]
WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL_HERE"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Update path as needed

# Fetch rating and game data
def fetch_user_stats(username):
    now = datetime.datetime.utcnow()
    start_of_week = now - datetime.timedelta(days=7)
    year = start_of_week.year
    month = start_of_week.month

    url_games = f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02d}"
    url_stats = f"https://api.chess.com/pub/player/{username}/stats"

    games_data = requests.get(url_games).json()
    stats_data = requests.get(url_stats).json()

    blitz_rating = stats_data.get("chess_blitz", {}).get("last", {}).get("rating", None)

    games = [g for g in games_data.get("games", []) if datetime.datetime.fromtimestamp(g["end_time"]) > start_of_week]
    wins = sum(1 for g in games if g.get("white", {}).get("username", "").lower() == username.lower() and g.get("white", {}).get("result") == "win" or
                                   g.get("black", {}).get("username", "").lower() == username.lower() and g.get("black", {}).get("result") == "win")
    losses = sum(1 for g in games if g.get("white", {}).get("username", "").lower() == username.lower() and g.get("white", {}).get("result") in ["checkmated", "timeout"] or
                                    g.get("black", {}).get("username", "").lower() == username.lower() and g.get("black", {}).get("result") in ["checkmated", "timeout"])

    return {
        "username": username,
        "games_played": len(games),
        "wins": wins,
        "losses": losses,
        "rating": blitz_rating or 0
    }

# Generate image

def generate_summary_image(players):
    img = Image.new("RGB", (1080, 1080), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_title = ImageFont.truetype(FONT_PATH, 60)
    font_body = ImageFont.truetype(FONT_PATH, 40)

    draw.text((30, 30), "Weekly Chess Summary ♟", fill="black", font=font_title)
    y = 150
    top_performer = max(players, key=lambda p: p['wins'])
    for player in players:
        text = f"{player['username']}: {player['rating']} ELO | {player['games_played']} games | {player['wins']}W/{player['losses']}L"
        draw.text((40, y), text, fill="black", font=font_body)
        y += 80

    draw.text((40, y + 40), f"🔥 Top Performer: {top_performer['username']} with {top_performer['wins']} wins!", fill="darkgreen", font=font_body)

    img.save("weekly_chess_summary.png")

# Send image to Discord

def send_to_discord():
    webhook = DiscordWebhook(url=WEBHOOK_URL)
    with open("weekly_chess_summary.png", "rb") as f:
        webhook.add_file(file=f.read(), filename="weekly_chess_summary.png")

    embed = DiscordEmbed(title="♟ Weekly Chess Summary", description="Here’s how everyone did this week:", color=242424)
    embed.set_image(url="attachment://weekly_chess_summary.png")
    webhook.add_embed(embed)
    response = webhook.execute()

if __name__ == "__main__":
    summary = [fetch_user_stats(user) for user in USERS]
    generate_summary_image(summary)
    send_to_discord()
