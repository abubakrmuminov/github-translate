
import discord
from discord import app_commands
from discord.ext import commands
from deep_translator import GoogleTranslator
from langdetect import detect
import logging
from typing import Optional
from utils.cache import cache
from utils.embeds import create_translation_embed
from gtts import gTTS
import io
import os
from config import Config

logger = logging.getLogger('TranslatorBot')

class Translation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Context Menus
        self.ctx_menu_translate = app_commands.ContextMenu(
            name="🌐 Translate Message",
            callback=self.context_translate
        )
        self.ctx_menu_quick = app_commands.ContextMenu(
            name="⚡ Quick Translate",
            callback=self.quick_translate
        )
        self.bot.tree.add_command(self.ctx_menu_translate)
        self.bot.tree.add_command(self.ctx_menu_quick)

    async def _process_translation(self, interaction: discord.Interaction, text: str, target_lang: str):
        await interaction.response.defer(ephemeral=True)
        
        # Detect language
        try:
            source_lang = detect(text)
        except:
            source_lang = "auto"
            
        # Check cache
        cache_hit = False
        translated_text = await cache.get_translation(text, source_lang, target_lang)
        
        if not translated_text:
            try:
                translated_text = GoogleTranslator(source='auto', target=target_lang).translate(text)
                await cache.set_translation(text, source_lang, target_lang, translated_text)
            except Exception as e:
                logger.error(f"Translation error: {e}")
                await interaction.followup.send("❌ Failed to translate message.", ephemeral=True)
                return
        else:
            cache_hit = True

        embed = create_translation_embed(
            original_text=text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            cache_hit=cache_hit
        )
        
        # View with buttons
        view = TranslationView(text, translated_text, target_lang)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    async def context_translate(self, interaction: discord.Interaction, message: discord.Message):
        if not message.content:
            await interaction.response.send_message("❌ No text content to translate.", ephemeral=True)
            return
            
        # Show language selection first
        view = LanguageSelectView(message.content, self)
        await interaction.response.send_message("Select target language:", view=view, ephemeral=True)

    async def quick_translate(self, interaction: discord.Interaction, message: discord.Message):
        if not message.content:
            await interaction.response.send_message("❌ No text content.", ephemeral=True)
            return
            
        # Get user settings
        settings = await cache.get_user_settings(interaction.user.id)
        target_lang = settings.get("preferred_language", "en") if settings else "en"
        
        await self._process_translation(interaction, message.content, target_lang)

    @app_commands.command(name="translate", description="Translate text")
    @app_commands.describe(text="Text to translate", target="Target language code (en, ru, ko, etc)")
    async def translate_cmd(self, interaction: discord.Interaction, text: str, target: Optional[str] = None):
        if not target:
             settings = await cache.get_user_settings(interaction.user.id)
             target = settings.get("preferred_language", "en") if settings else "en"
             
        await self._process_translation(interaction, text, target)


class LanguageSelectView(discord.ui.View):
    def __init__(self, text: str, cog: Translation):
        super().__init__()
        self.text = text
        self.cog = cog
        
        # Add Select
        select = discord.ui.Select(placeholder="Select Language...", min_values=1, max_values=1)
        
        for code, info in Config.SUPPORTED_LANGUAGES.items():
            select.add_option(label=info["name"], value=code, emoji=info["flag"])
            
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        target = interaction.data["values"][0]
        await self.cog._process_translation(interaction, self.text, target)

class TranslationView(discord.ui.View):
    def __init__(self, original: str, translated: str, lang_code: str):
        super().__init__()
        self.original = original
        self.translated = translated
        self.lang_code = lang_code

    @discord.ui.button(label="📢 Show to All", style=discord.ButtonStyle.secondary)
    async def share(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.channel.send(f"**Translation ({self.lang_code}):**\n{self.translated}")
            await interaction.response.send_message("Shared!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to send messages in this channel.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error sharing: {e}", ephemeral=True)

    @discord.ui.button(label="🔊 Listen", style=discord.ButtonStyle.secondary, emoji="🔈")
    async def listen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        try:
            tts = gTTS(text=self.translated, lang=self.lang_code)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            file = discord.File(fp, filename=f"pronunciation_{self.lang_code}.mp3")
            await interaction.followup.send(file=file, ephemeral=True)
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            await interaction.followup.send("❌ TTS not available for this language/text.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Translation(bot))
