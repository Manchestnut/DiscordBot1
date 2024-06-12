import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def top10(ctx, year: int, season: str):
    current_year = datetime.datetime.now().year
    if year < 2000 or year > current_year or season.lower() not in ["winter", "spring", "summer", "fall"]:
        await ctx.send("Please enter a valid year (2000 or later) and season (winter, spring, summer, fall)")
        return

    url = f"https://myanimelist.net/anime/season/{year}/{season.lower()}"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    animes = soup.find_all(class_="link-title")
    scores = soup.find_all(title="Score")
    genres = soup.find_all(class_="genres-inner")

    output = f"Top 10 Animes of {season.capitalize()} {year} (sorted by popularity)\n"
    for anime, score, genre in zip(animes[:10], scores[:10], genres[:10]):
        title = anime.text.strip()
        score_value = score.text.strip()
        link = anime.get("href").strip()
        genres_list = [g.text.strip() for g in genre.find_all("span")]
        genres_str = ", ".join(genres_list)
        output += f"\nTitle: {title} \nGenres: {genres_str} \nScore: {score_value} \n<{link}> \n"

    await ctx.send(output)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required arguments. Please provide both year and season. Example: `!top10 2023 summer`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument type. Make sure the year is a number and season is a valid string.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Unknown command. Please use a valid command. Example: `!top10 2023 summer`")
    else:
        await ctx.send("An error occurred. Please try again.")
    print(f"An error occurred: {error}")

if __name__ == "__main__":
    print("Starting bot...")
    bot.run(TOKEN)
