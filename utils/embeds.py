
import discord
from datetime import datetime
from typing import Optional

class EmbedColors:
    INFO = 0x3498db      
    SUCCESS = 0x2ecc71   
    ERROR = 0xe74c3c     
    WARNING = 0xf39c12   
    PURPLE = 0x9b59b6    
    TRANSLATION = 0x3498db
    LEVEL_UP = 0xf1c40f  
    QUIZ = 0x9b59b6      

def create_translation_embed(
    original_text: str,
    translated_text: str,
    source_lang: str,
    target_lang: str,
    cache_hit: bool = False,
    cultural_note: Optional[str] = None
) -> discord.Embed:
    flags = {
        "ru": "🇷🇺", "en": "🇬🇧", "ko": "🇰🇷",
        "pt": "🇵🇹", "es": "🇪🇸"
    }
    
    source_flag = flags.get(source_lang, "🌍")
    target_flag = flags.get(target_lang, "🌍")
    
    lang_names = {
        "ru": "Russian", "en": "English",
        "ko": "Korean", "pt": "Portuguese",
        "es": "Spanish"
    }
    
    source_name = lang_names.get(source_lang, source_lang.upper())
    target_name = lang_names.get(target_lang, target_lang.upper())
    
    embed = discord.Embed(
        title="🌐 Translate Message",
        color=EmbedColors.TRANSLATION,
        timestamp=datetime.utcnow()
    )
    
    # Original
    orig_text = original_text if len(original_text) <= 500 else original_text[:497] + "..."
    embed.add_field(
        name=f"📝 Original ({source_flag} {source_name}):",
        value=orig_text,
        inline=False
    )
    
    # Translation
    trans_text = translated_text if len(translated_text) <= 500 else translated_text[:497] + "..."
    embed.add_field(
        name=f"🎯 Translation ({target_flag} {target_name}):",
        value=trans_text,
        inline=False
    )
    
    if cultural_note:
        embed.add_field(
            name="⚠️ Cultural Context:",
            value=cultural_note[:500],
            inline=False
        )
    
    cache_status = "✅" if cache_hit else "⚡"
    embed.set_footer(
        text=f"Cached: {cache_status}"
    )
    
    return embed

def get_flag(lang_code: str) -> str:
    flags = {
        "ru": "🇷🇺", "en": "🇬🇧", "ko": "🇰🇷",
        "pt": "🇵🇹", "es": "🇪🇸"
    }
    return flags.get(lang_code, "🌍")

def create_profile_embed(user: discord.User, profile_data: dict) -> discord.Embed:
    embed = discord.Embed(
        title=f"👤 Profile: {user.display_name}",
        color=EmbedColors.INFO,
        timestamp=datetime.utcnow()
    )
    
    if user.avatar:
        embed.set_thumbnail(url=user.avatar.url)
    
    # Native Language
    native_langs = [
        f"{get_flag(lang['code'])} {lang['name']} (Native)"
        for lang in profile_data.get("native_languages", [])
    ]
    if native_langs:
        embed.add_field(
            name="🌍 Native Language:",
            value="\n".join(native_langs),
            inline=False
        )
    
    # Fluent
    fluent_langs = [
        f"{get_flag(lang['code'])} {lang['name']} ({lang.get('level', '')})"
        for lang in profile_data.get("fluent_languages", [])
    ]
    if fluent_langs:
        embed.add_field(
            name="📚 Fluent in:",
            value="\n".join(fluent_langs),
            inline=False
        )
    
    # Learning
    learning_langs = [
        f"{get_flag(lang['code'])} {lang['name']} ({lang.get('level', '')}) 🔄"
        for lang in profile_data.get("learning_languages", [])
    ]
    if learning_langs:
        embed.add_field(
            name="📖 Learning:",
            value="\n".join(learning_langs),
            inline=False
        )
    
    # Wants Practice
    practice_langs = [
        get_flag(lang) for lang in profile_data.get("wants_practice", [])
    ]
    if practice_langs:
        embed.add_field(
            name="🎯 Wants to Practice:",
            value=" ".join(practice_langs),
            inline=False
        )
    
    # Statistics
    stats = profile_data.get("stats", {})
    embed.add_field(
        name="📊 Statistics:",
        value=f"• Translations: {stats.get('translations', 0)}\n"
              f"• Days on Server: {stats.get('days_on_server', 0)}\n"
              f"• Level: {stats.get('level_name', 'Novice')} (Lvl {stats.get('level', 1)})",
        inline=False
    )
    
    return embed
