import requests
import os
from interactions import slash_command, SlashContext, Client, Intents, listen

bot = Client(intents=Intents.DEFAULT)

@listen()
async def on_ready() -> None:
    print("Ready")
    print(f"This bot is owned by {bot.owner}")


@slash_command("server_ip", description="Get the IP-address for the server.")
async def get_server_ip(ctx: SlashContext) -> None:
    ip = requests.get("https://api.ipify.org").content.decode('utf8')
    await ctx.send(f"IP: {ip}")


if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN", "")
    if TOKEN != "":
        bot.start(TOKEN)