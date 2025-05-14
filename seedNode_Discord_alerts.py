import requests
import schedule
import time
import socket
import subprocess
from discord_webhook import DiscordWebhook
from datetime import datetime

# Discord webhook URL for alerts
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"

# Function to send Discord alerts
def send_discord_alert(message):
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=message)
    response = webhook.execute()

# Function to perform the health check
def health_check():
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
        
        # If "ANSWER SECTION" is found in the result, the DNS server is responding
        if "ANSWER SECTION" not in result.stdout:
            raise Exception("No answer from DNS server.")
        
        print(f"Health check passed at {datetime.now()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        # Send alert to Discord if the server is down or unresponsive
        message = f"🚨 **Alert**: DNS Seeder is down or unresponsive at {datetime.now()}. Error: {e}"
        send_discord_alert(message)

# Schedule the health check to run every 5 minutes
schedule.every(5).minutes.do(health_check)

# Run the scheduler
if __name__ == "__main__":
    print("Health check monitoring started...")
    while True:
        schedule.run_pending()
        time.sleep(1)
