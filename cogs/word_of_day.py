
import discord
from discord import app_commands
from discord.ext import commands, tasks
import logging
from datetime import datetime
from typing import Optional
from config import Config
from utils.database import Database
import random # For mock data if DB is empty

logger = logging.getLogger('TranslatorBot')

class WordOfDay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.daily_word_task.start() # Start loop

    def cog_unload(self):
        self.daily_word_task.cancel()

    @tasks.loop(hours=24)
    async def daily_word_task(self):
        # Implementation for scheduled posting
        # 1. Select word from DB
        # 2. Post to configured channels
        pass

    @daily_word_task.before_loop
    async def before_daily_word(self):
        await self.bot.wait_until_ready()
        # Wait until 10:00 UTC
        # ...

    @app_commands.command(name="word", description="Get the Word of the Day")
    @app_commands.describe(language="Language code", category="Category (common, slang, etc)")
    async def word(self, interaction: discord.Interaction, language: Optional[str] = None, category: Optional[str] = None):
        if not language:
             # Get user preference
             # ...
             language = "en"
             
        # Mock data for demonstration since we don't have a populated DB yet
        mock_words = {
            "en": {"word": "Serendipity", "meaning": "The occurrence of events by chance in a happy or beneficial way.", "pronunciation": "ˌser.ənˈdɪp.ə.ti"},
            "ru": {"word": "Уют", "meaning": "Comfort and warmth of the home atmosphere.", "pronunciation": "oo-yoot"},
            "ko": {"word": "눈치 (Nunchi)", "meaning": "The subtle art of looking at others' emotions and gauging the situation.", "pronunciation": "noon-chee"},
        }
        
        word_data = mock_words.get(language, mock_words["en"])
        
        embed = discord.Embed(
            title=f"📚 Word of the Day: {word_data['word']}",
            description=word_data['meaning'],
            color=0x3498db
        )
        embed.add_field(name="🔊 Pronunciation", value=word_data['pronunciation'])
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="word_subscribe", description="Subscribe to daily words in DM")
    async def subscribe(self, interaction: discord.Interaction):
        # Toggle subscription in DB
        await interaction.response.send_message("✅ Subscribed to Word of the Day!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(WordOfDay(bot))
