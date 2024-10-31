import socket

import interactions
import requests
import os
from interactions import slash_command, SlashContext, Client, Intents, listen, File, slash_str_option, OptionType
from io import BytesIO

import trusetekst
from trusetekst import TRUSE_PATH

HOSTNAME: str = "host.docker.internal"


class JyssesService:
    Jellyfin = 0
    Audiobookshelf = 1
    Radarr = 2
    Sonarr = 3
    Prowlarr = 4
    Sabnzbd = 5
    Jellyseerr = 6
    Bazarr = 7
    JFAGo = 8


SERVICE_PORT: dict = {
    JyssesService.Jellyfin: 8096,
    JyssesService.Audiobookshelf: 13378,
    JyssesService.Radarr: 7878,
    JyssesService.Sonarr: 8989,
    JyssesService.Prowlarr: 9696,
    JyssesService.Sabnzbd: 8080,
    JyssesService.Jellyseerr: 5055,
    JyssesService.Bazarr: 6767,
    JyssesService.JFAGo: 8056
}

SERVICE_NAME: dict = {
    JyssesService.Jellyfin: "Jellyfin",
    JyssesService.Audiobookshelf: "Audiobookshelf",
    JyssesService.Radarr: "Radarr",
    JyssesService.Sonarr: "Sonarr",
    JyssesService.Prowlarr: "Prowlarr",
    JyssesService.Sabnzbd: "sabnzbd",
    JyssesService.Jellyseerr: "Jellyseerr",
    JyssesService.Bazarr: "Bazarr",
    JyssesService.JFAGo: "JFA-Go"
}

bot = Client(intents=Intents.DEFAULT)


@listen()
async def on_ready() -> None:
    print("Ready")
    print(f"This bot is owned by {bot.owner}")


@slash_command("server_ip", description="Get the IP-address for the server.")
async def get_server_ip(ctx: SlashContext) -> None:
    ip = requests.get("https://api.ipify.org").content.decode('utf8')
    await ctx.send(f"IP: {ip}")


@slash_command("server_status", description="Check status of different Jysses services")
async def get_server_status(ctx: SlashContext) -> None:
    results: dict = {}
    await ctx.defer()
    for k, name in SERVICE_NAME.items():
        results[k] = check_port(SERVICE_PORT[k])

    msg: str = "**STATUS**:\n"
    for k, v in results.items():
        msg += f"{SERVICE_NAME[k]}: {':green_circle:' if v else ':red_circle:'}\n"

    await ctx.send(msg)


@slash_command("trusetext", description="Trusetekst, du vet.")
@slash_str_option(
    name="text",
    description="Teksten som skal vises"
)
async def generate_trusetext(ctx: SlashContext, text: str) -> None:
    img = trusetekst.get_trusetext(
        text, trusetekst.fonts["Truckin"], 32, trusetekst.COLORS["red"], trusetekst.V_ALIGN_BOTTOM, trusetekst.H_ALIGN_CENTER
    )
    f = None

    img_binary = BytesIO()
    img.save(img_binary, format="PNG")
    img_binary.seek(0)

    # with open(TRUSE_PATH, "r") as f:
    await ctx.send(
        "", file=File(img_binary, file_name="truse.png")
    )
    # f.close()


def check_port(port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect((HOSTNAME, port))
    except Exception as e:
        print(e)
        return False
    else:
        print(f"Port {port} was OK.")
        sock.close()
        return True


if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN", "")
    if TOKEN != "":
        bot.start(TOKEN)

