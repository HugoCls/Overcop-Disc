import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging as log
from bs4 import BeautifulSoup
import httpx
import json

log_format = "%(asctime)s [%(levelname)s] %(name)s:%(filename)s - %(message)s"

log.basicConfig(format=log_format)
log.getLogger().setLevel(log.INFO)

load_dotenv()

TOKEN = os.getenv("discord_token")
SERVER_ID = os.getenv("discord_server_id")


def retrieve_images(url: str):
    url = url.strip('https://')

    url = "https://" + url

    try:
        r = httpx.get(url)

        soup = BeautifulSoup(r.text, "html.parser")

        json_scripts = soup.find_all('script', {'type': 'application/ld+json'})#, 'text': lambda text: text is not None and "'image':'https://cdn.shopify.com/s/files/" in text})

        for i, json_str in enumerate(json_scripts):
            if 'image' in json.loads(json_str.text).keys():
                break
        
        json_content = json.loads(json_str.text)

        images_links = json_content['image']

        return images_links
        
    except:
        return "Bad url"


bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        log.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        log.info(e)

@bot.tree.command(name="images", description="From a WeTheNew Shoe url, sends back all the images links to the user")#, guild=discord.Object(id=SERVER_ID))
@app_commands.describe(url="some_url")
async def images(interaction: discord.Interaction, url: str):
    images_links = retrieve_images(url)

    if images_links:
        # Send the first message as a response
        await interaction.response.send_message(images_links[0])

        # Send the remaining images in the same channel but not as a response
        for image_link in images_links[1:]:
            await interaction.followup.send(image_link)

    else:
        await interaction.response.send_message("Bad URL")

bot.run(TOKEN)