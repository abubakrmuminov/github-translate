
import discord
from discord import app_commands
from discord.ext import commands, tasks
import logging
from typing import Optional, List
from config import Config
from utils.database import Database
from utils.embeds import create_profile_embed, EmbedColors
from utils.cache import cache

logger = logging.getLogger('TranslatorBot')

class LanguageExchange(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.voice_room_manager.start() # Uncomment to enable auto-voice rooms

    @app_commands.command(name="profile", description="View or edit your language profile")
    @app_commands.describe(user="User to view (optional)")
    async def profile(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        target_user = user or interaction.user
        
        # Determine if it's "my" profile for editing
        is_self = target_user.id == interaction.user.id
        
        # 1. Get profile data from DB
        profile_data = await self.get_fake_profile_data(target_user.id) # Replace with DB call
        
        embed = create_profile_embed(target_user, profile_data)
        
        view = ProfileView(target_user.id, is_self)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="find_partner", description="Find a language exchange partner")
    @app_commands.describe(i_speak="Language you speak (native/fluent)", i_learn="Language you want to practice")
    async def find_partner(self, interaction: discord.Interaction, i_speak: str, i_learn: str):
        await interaction.response.defer(ephemeral=True)
        
        # Mock search logic
        # In reality: SELECT * FROM user_languages WHERE ...
        
        embed = discord.Embed(title=f"🤝 Found Partners ({i_speak} ↔️ {i_learn})", color=EmbedColors.SUCCESS)
        embed.description = "Here are some matching users:"
        
        # Mock results
        embed.add_field(
            name="1️⃣ @KoreanUser",
            value=f"🇰🇷 Native | 🇷🇺 Learning (A2)\nmatch: ⭐ Perfect!\n[Message]",
            inline=False
        )
        embed.add_field(
             name="2️⃣ @AnotherUser",
             value=f"🇰🇷 Fluent (C1) | 🇷🇺 Learning (B1)\nmatch: ✅ Good\n[Message]",
             inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not Config.FEATURES["voice_rooms_enabled"]: return
        
        # Logic for creating temporary voice channels based on language
        # 1. Check if user joined a "Join to Create" channel or general logic
        # 2. Check user's preferred language
        # 3. Create/Join language specific room
        pass

    async def get_fake_profile_data(self, user_id: int):
        # Determine "level" based on calculations
        return {
            "native_languages": [{"code": "ru", "name": "Russian"}],
            "fluent_languages": [{"code": "en", "name": "English", "level": "C1"}],
            "learning_languages": [{"code": "ko", "name": "Korean", "level": "B1"}],
            "wants_practice": ["ko", "es"],
            "stats": {"translations": 1234, "days_on_server": 45, "level": 5, "level_name": "Polyglot"},
            "badges": ["🌟", "💯", "🔥", "🌍"]
        }

class ProfileView(discord.ui.View):
    def __init__(self, user_id: int, is_self: bool):
        super().__init__()
        self.user_id = user_id
        
        if is_self:
            self.add_item(discord.ui.Button(label="✏️ Edit Profile", style=discord.ButtonStyle.primary, custom_id="edit_profile"))
        
        self.add_item(discord.ui.Button(label="🤝 Find Partner", style=discord.ButtonStyle.secondary, custom_id="find_partner_btn"))

async def setup(bot):
    await bot.add_cog(LanguageExchange(bot))
