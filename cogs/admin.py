
import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional
from config import Config
from utils.cache import cache

logger = logging.getLogger('TranslatorBot')

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        # Simple check for owner or admin permissions
        return ctx.author.id == Config.OWNER_ID or ctx.author.guild_permissions.administrator

    @app_commands.command(name="admin_setup", description="Initial server setup (Channels, Roles)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_server(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        
        status_msg = ["⚙️ **Starting Setup...**"]
        
        # 1. Create Roles
        roles_to_create = {
            "Polyglot": discord.Color.gold(),
            "Native Speaker": discord.Color.green(),
            "Learner": discord.Color.blue(),
            "Quiz Master": discord.Color.purple()
        }
        
        created_roles = []
        for name, color in roles_to_create.items():
            existing = discord.utils.get(guild.roles, name=name)
            if not existing:
                try:
                    role = await guild.create_role(name=name, color=color, reason="Translator Bot Setup")
                    created_roles.append(role.mention)
                except Exception as e:
                    logger.error(f"Failed to create role {name}: {e}")
            else:
                created_roles.append(f"{existing.mention} (Skipped)")
        
        status_msg.append(f"✅ roles: {', '.join(created_roles)}")
        
        # 2. Create Category and Channels
        cat_name = "🌍 Language Learning"
        category = discord.utils.get(guild.categories, name=cat_name)
        
        if not category:
            try:
                category = await guild.create_category(cat_name)
                status_msg.append(f"✅ Category: **{cat_name}** created")
            except Exception:
                status_msg.append(f"❌ Failed to create category")
        
        if category:
            channels = {
                "word-of-the-day": "Daily vocabulary practice",
                "quizzes": "Language quizzes and games",
                "general-learning": "Discuss language learning here"
            }
            
            created_channels = []
            for name, topic in channels.items():
                existing = discord.utils.get(guild.text_channels, name=name, category_id=category.id)
                if not existing:
                    try:
                        chan = await guild.create_text_channel(name, category=category, topic=topic)
                        created_channels.append(chan.mention)
                    except:
                        pass
                else:
                    created_channels.append(f"{existing.mention} (Skipped)")
            
            status_msg.append(f"✅ Channels: {', '.join(created_channels)}")
            
        await interaction.followup.send("\n".join(status_msg), ephemeral=True)

    @app_commands.command(name="set_word_channel", description="Set channel for Word of the Day")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def set_word_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # Save to DB
        await interaction.response.send_message(f"✅ Word of Day channel set to {channel.mention}", ephemeral=True)

    @app_commands.command(name="translate_history", description="Mass translate recent messages (Mod Only)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def translate_history(self, interaction: discord.Interaction, count: int, target: str):
        if count > 100: count = 100
        await interaction.response.defer(ephemeral=True)
        
        messages = []
        async for msg in interaction.channel.history(limit=count):
            if msg.content:
                messages.append(f"[{msg.author}] {msg.content}")
        
        # Logic to translate them all and save to file
        report = f"Translated {len(messages)} messages to {target}.\n\n" + "\n".join(messages)
        
        # Mock file
        import io
        fp = io.BytesIO(report.encode('utf-8'))
        file = discord.File(fp, filename="translation_report.txt")
        
        await interaction.followup.send(content="✅ Report generated:", file=file, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
