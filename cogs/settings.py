
import discord
from discord import app_commands
from discord.ext import commands
import logging
from config import Config
from utils.cache import cache

logger = logging.getLogger('TranslatorBot')

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="settings", description="Configure your preferences")
    async def settings(self, interaction: discord.Interaction):
        # Fetch current settings (mock or cache)
        user_settings = await cache.get_user_settings(interaction.user.id)
        if not user_settings:
            user_settings = {"preferred_language": "en"}
            
        current_lang = user_settings.get("preferred_language", "en")
        lang_info = Config.SUPPORTED_LANGUAGES.get(current_lang, {"name": "English", "flag": "🇬🇧"})
        
        embed = discord.Embed(title="⚙️ Settings", color=0x3498db)
        embed.add_field(name="🌍 Primary Language", value=f"{lang_info['flag']} {lang_info['name']}")
        
        view = SettingsView(current_lang)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class SettingsView(discord.ui.View):
    def __init__(self, current_lang: str):
        super().__init__()
        
        # Language Select
        select = discord.ui.Select(placeholder="Change Language...", min_values=1, max_values=1)
        for code, info in Config.SUPPORTED_LANGUAGES.items():
            select.add_option(
                label=info["name"], 
                value=code, 
                emoji=info["flag"],
                default=(code == current_lang)
            )
        select.callback = self.lang_callback
        self.add_item(select)

    async def lang_callback(self, interaction: discord.Interaction):
        lang = interaction.data["values"][0]
        # Save to cache/db
        current = await cache.get_user_settings(interaction.user.id) or {}
        current["preferred_language"] = lang
        await cache.set_user_settings(interaction.user.id, current)
        
        await interaction.response.send_message(f"✅ Language set to {lang}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Settings(bot))
