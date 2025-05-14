import requests
import schedule
import time
import socket
import subprocess
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get environment variables from the .env file
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# State flags
is_up = True  # Tracks whether the seeder is currently up or down
retry_count = 0
MAX_RETRIES = 3  # Retry count before sending alerts

# Function to send Discord alerts with embed
def send_discord_alert(embed):
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
    webhook.add_embed(embed)
    response = webhook.execute()

# Function to create an embed message
def create_embed(title, description, color):
    embed = DiscordEmbed(title=title, description=description, color=color)
    embed.set_footer(text="Health Check Monitor")
    embed.set_timestamp()
    return embed

# Function to perform the health check
def health_check():
    global is_up, retry_count

    try:
        # Check if DNS port 8053 is open and responsive (using socket)
        sock = socket.create_connection(("localhost", 8053), timeout=10)
        sock.close()

        # Perform a dig query to check if the server responds
        result = subprocess.run(
            ["dig", "A", "seeder.adventurecoin.quest", "@localhost", "-p", "8053"],
            capture_output=True,
            text=True
        )
        
        # If "ANSWER SECTION" is not found, raise an exception
        if "ANSWER SECTION" not in result.stdout:
            raise Exception("No answer from DNS server.")

        print(f"Health check passed at {datetime.now()}")

        # If the server was previously down, send an alert that it's back up
        if not is_up:
            embed = create_embed(
                "✅ **DNS Seeder is Back Online**",
                f"The DNS Seeder is now online and responding to requests at {datetime.now()}.",
                0x2ECC71  # Green
            )
            send_discord_alert(embed)
            is_up = True  # Update state to up

        # Reset the retry count on a successful check
        retry_count = 0

    except Exception as e:
        print(f"Health check failed: {e}")
        retry_count += 1
        
        if retry_count <= MAX_RETRIES:
            print(f"Retrying... ({retry_count}/{MAX_RETRIES})")
        else:
            if is_up:
                embed = create_embed(
                    "🚨 **DNS Seeder is Down**",
                    f"The DNS Seeder is down or unresponsive at {datetime.now()}.\n\nError: `{e}`",
                    0xE74C3C  # Red
                )
                send_discord_alert(embed)
                is_up = False  # Update state to down

# Schedule the health check to run every 5 minutes
schedule.every(5).minutes.do(health_check)

# Run the scheduler
if __name__ == "__main__":
    print("Health check monitoring started...")

    # Send startup message once
    startup_embed = create_embed(
        "🛡️ DNS Seeder Monitor Started",
        f"Monitoring has **started** at {datetime.now()}.\nHealth checks run every 5 minutes.",
        0x3498DB  # Blue
    )
    send_discord_alert(startup_embed)

    while True:
        schedule.run_pending()
        time.sleep(1)
