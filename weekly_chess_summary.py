import requests
import datetime
import json
from PIL import Image, ImageDraw, ImageFont
from discord_webhook import DiscordWebhook, DiscordEmbed

# Load secrets from JSON
with open("secrets.json", "r") as f:
    secrets = json.load(f)

USERS = secrets["users"]
WEBHOOK_URL = secrets["webhook_url"]
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Update if needed

def fetch_user_stats(username):
    now = datetime.datetime.now(datetime.timezone.utc)
    start_of_week = now - datetime.timedelta(days=7)

    archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    archives_response = requests.get(archives_url)
    archives = archives_response.json().get("archives", [])
    if not archives:
        print(f"No archives found for {username}")
        return default_stats(username)

    latest_archive_url = archives[-1]
    games_response = requests.get(latest_archive_url)
    games_data = games_response.json()

    stats_url = f"https://api.chess.com/pub/player/{username}/stats"
    stats_data = requests.get(stats_url).json()

    blitz = stats_data.get("chess_blitz", {}).get("last", {}).get("rating", 0)
    rapid = stats_data.get("chess_rapid", {}).get("last", {}).get("rating", 0)
    bullet = stats_data.get("chess_bullet", {}).get("last", {}).get("rating", 0)

    games = [g for g in games_data.get("games", []) if datetime.datetime.fromtimestamp(g["end_time"], tz=datetime.timezone.utc) > start_of_week]

    wins = sum(1 for g in games if is_win(g, username))
    losses = sum(1 for g in games if is_loss(g, username))

    top_game = max(games, key=lambda g: g.get("white", {}).get("rating", 0) if g.get("white", {}).get("username", "").lower() == username.lower() else g.get("black", {}).get("rating", 0), default=None)
    top_game_url = top_game.get("url", "") if top_game else ""

    return {
        "username": username,
        "games_played": len(games),
        "wins": wins,
        "losses": losses,
        "rating_blitz": blitz,
        "rating_rapid": rapid,
        "rating_bullet": bullet,
        "highlight_game": top_game_url
    }

def is_win(game, username):
    return (game.get("white", {}).get("username", "").lower() == username.lower() and game.get("white", {}).get("result") == "win") or            (game.get("black", {}).get("username", "").lower() == username.lower() and game.get("black", {}).get("result") == "win")

def is_loss(game, username):
    return (game.get("white", {}).get("username", "").lower() == username.lower() and game.get("white", {}).get("result") in ["checkmated", "timeout"]) or            (game.get("black", {}).get("username", "").lower() == username.lower() and game.get("black", {}).get("result") in ["checkmated", "timeout"])

def default_stats(username):
    return {
        "username": username,
        "games_played": 0,
        "wins": 0,
        "losses": 0,
        "rating_blitz": 0,
        "rating_rapid": 0,
        "rating_bullet": 0,
        "highlight_game": ""
    }

def generate_summary_image(players):
    img = Image.new("RGB", (1080, 1080), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_title = ImageFont.truetype(FONT_PATH, 56)
    font_body = ImageFont.truetype(FONT_PATH, 36)

    draw.text((30, 30), "Weekly Chess Summary ♟", fill="black", font=font_title)
    y = 120
    top_performer = max(players, key=lambda p: p['wins'], default=None)

    for player in players:
        lines = [
            f"{player['username']}: {player['games_played']} games | {player['wins']}W/{player['losses']}L",
            f"Blitz: {player['rating_blitz']} | Rapid: {player['rating_rapid']} | Bullet: {player['rating_bullet']}"
        ]
        for line in lines:
            draw.text((40, y), line, fill="black", font=font_body)
            y += 50
        y += 20

    if top_performer:
        draw.text((40, y + 30), f"🔥 Top Performer: {top_performer['username']} with {top_performer['wins']} wins!", fill="darkgreen", font=font_body)

    img.save("weekly_chess_summary.png")

def send_to_discord(players):
    webhook = DiscordWebhook(url=WEBHOOK_URL)
    with open("weekly_chess_summary.png", "rb") as f:
        webhook.add_file(file=f.read(), filename="weekly_chess_summary.png")

    embed = DiscordEmbed(title="♟ Weekly Chess Summary", description="Your game report this week:", color=242424)
    embed.set_image(url="attachment://weekly_chess_summary.png")

    for player in players:
        if player["highlight_game"]:
            embed.add_embed_field(name=f"{player['username']}'s Highlight 🎯", value=f"[View Game]({player['highlight_game']})", inline=False)

    webhook.add_embed(embed)
    webhook.execute()

if __name__ == "__main__":
    summary = [fetch_user_stats(user) for user in USERS]
    generate_summary_image(summary)
    send_to_discord(summary)
