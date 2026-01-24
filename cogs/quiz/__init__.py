
import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Literal, Optional
import random
import asyncio
from deep_translator import GoogleTranslator
from deep_translator import GoogleTranslator
from config import Config
from cogs.quiz.database import QuizDatabase
from cogs.quiz.quiz_data import (
    get_random_word, get_all_words_except, DIFFICULTY_POINTS, 
    STREAK_BONUS, get_xp_for_next_level
)
import time

logger = logging.getLogger('TranslatorBot')

class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = QuizDatabase()
        self.active_multiplayer_games = {}  # channel_id: game_data
        
    async def cog_load(self):
        """Initialize database when cog loads"""
        await self.db.initialize()
        logger.info("Quiz database initialized")

    @app_commands.command(name="quiz", description="Start a language quiz with leveling system")
    @app_commands.describe(
        mode="Solo or Multiplayer mode",
        language="Target language to practice",
        difficulty="Difficulty level (affects XP rewards)"
    )
    @app_commands.choices(language=[
        app_commands.Choice(name=lang_data["name"], value=code)
        for code, lang_data in Config.SUPPORTED_LANGUAGES.items()
    ])
    async def quiz(
        self, 
        interaction: discord.Interaction, 
        mode: Literal["solo", "multiplayer"], 
        language: str, 
        difficulty: Literal["easy", "medium", "hard"] = "medium"
    ):
        await interaction.response.defer(ephemeral=(mode == "solo"))
        
        # Get user data
        user = await self.db.get_user(interaction.user.id, interaction.user.name)
        
        # Generate question
        word, category = get_random_word(difficulty)
        
        try:
            # Correct answer
            correct_translation = GoogleTranslator(source='en', target=language).translate(word)
            
            # Wrong answers
            wrong_words = get_all_words_except(difficulty, word, 3)
            wrong_translations = [
                GoogleTranslator(source='en', target=language).translate(w) 
                for w in wrong_words
            ]
        except Exception as e:
            logger.error(f"Quiz generation error: {e}")
            await interaction.followup.send("❌ Failed to generate quiz. Try again.", ephemeral=True)
            return

        # Prepare options
        options = [correct_translation] + wrong_translations
        random.shuffle(options)
        correct_index = options.index(correct_translation)
        
        # Calculate potential XP
        base_xp = DIFFICULTY_POINTS[difficulty]
        
        # Create embed
        embed = discord.Embed(
            title=f"🎮 Quiz: {Config.SUPPORTED_LANGUAGES[language]['flag']} {Config.SUPPORTED_LANGUAGES[language]['name']}",
            color=self._get_difficulty_color(difficulty)
        )
        embed.add_field(
            name=f"📖 Translate ({difficulty.upper()}):",
            value=f"**{word}**",
            inline=False
        )
        embed.add_field(
            name="📊 Your Stats",
            value=f"Level: **{user['level']}** | XP: **{user['xp']}** | Streak: **{user['current_streak']}** 🔥",
            inline=False
        )
        embed.add_field(
            name="💰 Reward",
            value=f"Base: **{base_xp} XP** {'+ Streak bonus!' if user['current_streak'] >= 3 else ''}",
            inline=False
        )
        embed.set_footer(text=f"Category: {category.replace('_', ' ').title()} | ⏱️ You have 30 seconds!")
        
        # Multiplayer mode
        if mode == "multiplayer":
            self.active_multiplayer_games[interaction.channel_id] = {
                'participants': {},
                'correct_index': correct_index,
                'word': word,
                'correct_translation': correct_translation,
                'language': language,
                'difficulty': difficulty
            }
        
        view = QuizView(
            self.db,
            options, 
            correct_index, 
            word, 
            correct_translation,
            difficulty,
            language,
            user_id=interaction.user.id,
            is_multiplayer=(mode == "multiplayer"),
            game_data=self.active_multiplayer_games.get(interaction.channel_id)
        )
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=(mode == "solo"))
        
        # Auto-disable after timeout
        await asyncio.sleep(30)
        if not view.answered:
            view.stop()
            for item in view.children:
                item.disabled = True
            
            timeout_embed = discord.Embed(
                title="⏱️ Time's Up!",
                description=f"The correct answer was: **{correct_translation}**",
                color=0xe74c3c
            )
            
            try:
                if mode == "solo":
                    await interaction.edit_original_response(embed=timeout_embed, view=view)
                else:
                    # For multiplayer, send as new message
                    await interaction.channel.send(embed=timeout_embed)
            except:
                pass

    @app_commands.command(name="profile", description="View your quiz profile and statistics")
    async def profile(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        target_user = user or interaction.user
        
        stats = await self.db.get_user_stats(target_user.id)
        achievements = await self.db.get_user_achievements(target_user.id)
        
        # Calculate progress to next level
        current_level, next_level_xp, xp_needed = get_xp_for_next_level(stats['xp'])
        
        embed = discord.Embed(
            title=f"📊 {target_user.name}'s Quiz Profile",
            color=0x3498db
        )
        
        # Main stats
        embed.add_field(
            name="🎯 Level & XP",
            value=f"**Level {stats['level']}**\n{stats['xp']} XP" + 
                  (f"\n{xp_needed} XP to Level {current_level + 1}" if xp_needed else "\n**MAX LEVEL**"),
            inline=True
        )
        
        embed.add_field(
            name="🔥 Streaks",
            value=f"Current: **{stats['current_streak']}**\nBest: **{stats['best_streak']}**",
            inline=True
        )
        
        embed.add_field(
            name="🏆 Global Rank",
            value=f"**#{stats['rank']}**",
            inline=True
        )
        
        # Quiz stats
        embed.add_field(
            name="📚 Quiz Statistics",
            value=f"Total: **{stats['total_questions']}**\n" +
                  f"✅ Correct: **{stats['correct_answers']}**\n" +
                  f"❌ Wrong: **{stats['wrong_answers']}**\n" +
                  f"Accuracy: **{stats['accuracy']}%**",
            inline=True
        )
        
        # Achievements
        if achievements:
            achievements_text = "\n".join(achievements[:5])  # Show first 5
            if len(achievements) > 5:
                achievements_text += f"\n*...and {len(achievements) - 5} more*"
        else:
            achievements_text = "*No achievements yet*"
        
        embed.add_field(
            name=f"🏅 Achievements ({len(achievements)})",
            value=achievements_text,
            inline=True
        )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        embed.set_footer(text=f"Keep learning to unlock more achievements!")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="View the top quiz players")
    @app_commands.describe(by="Sort by XP or Best Streak")
    async def leaderboard(
        self, 
        interaction: discord.Interaction,
        by: Literal["xp", "streak"] = "xp"
    ):
        await interaction.response.defer()
        
        leaders = await self.db.get_leaderboard(limit=10, by=by)
        
        if not leaders:
            await interaction.followup.send("No players yet! Be the first to take a quiz!")
            return
        
        embed = discord.Embed(
            title=f"🏆 Top 10 Players {'(by XP)' if by == 'xp' else '(by Streak)'}",
            color=0xf39c12
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        leaderboard_text = ""
        for i, player in enumerate(leaders, 1):
            medal = medals[i-1] if i <= 3 else f"**{i}.**"
            
            if by == "xp":
                stat = f"Level {player['level']} • {player['xp']} XP"
            else:
                stat = f"Streak: {player['best_streak']} 🔥"
            
            try:
                user = await self.bot.fetch_user(player['user_id'])
                username = user.name
            except:
                username = player['username'] or "Unknown"
            
            leaderboard_text += f"{medal} **{username}**\n{stat}\n\n"
        
        embed.description = leaderboard_text
        embed.set_footer(text="Keep practicing to climb the ranks!")
        
        await interaction.followup.send(embed=embed)

    def _get_difficulty_color(self, difficulty: str) -> int:
        colors = {
            "easy": 0x2ecc71,    # Green
            "medium": 0xf39c12,  # Orange
            "hard": 0xe74c3c     # Red
        }
        return colors.get(difficulty, 0x3498db)


class QuizView(discord.ui.View):
    def __init__(
        self, 
        db: QuizDatabase,
        options: list, 
        correct_index: int, 
        original_word: str, 
        correct_word: str,
        difficulty: str,
        language: str,
        user_id: int,
        is_multiplayer: bool = False,
        game_data: dict = None
    ):
        super().__init__(timeout=30)
        self.db = db
        self.correct_index = correct_index
        self.original_word = original_word
        self.correct_word = correct_word
        self.difficulty = difficulty
        self.language = language
        self.user_id = user_id
        self.is_multiplayer = is_multiplayer
        self.game_data = game_data
        self.answered = False
        self.start_time = time.time()
        
        # Create buttons
        for i, option in enumerate(options):
            button = discord.ui.Button(
                label=option, 
                style=discord.ButtonStyle.secondary, 
                custom_id=str(i)
            )
            button.callback = self.check_answer
            self.add_item(button)

    async def check_answer(self, interaction: discord.Interaction):
        # Prevent double answers in solo mode
        if not self.is_multiplayer and self.answered:
            await interaction.response.send_message("You already answered!", ephemeral=True)
            return
        
        # In multiplayer, track who answered
        if self.is_multiplayer:
            if interaction.user.id in self.game_data['participants']:
                await interaction.response.send_message("You already answered!", ephemeral=True)
                return
        
        self.answered = True
        selected_index = int(interaction.data["custom_id"])
        is_correct = (selected_index == self.correct_index)
        
        # Calculate time bonus (faster = more XP, max 5 seconds bonus)
        time_taken = time.time() - self.start_time
        time_bonus = max(0, int(5 - (time_taken / 6)))  # 0-5 bonus XP
        
        # Calculate XP
        base_xp = DIFFICULTY_POINTS[self.difficulty]
        
        # Get user stats for streak bonus
        user = await self.db.get_user(interaction.user.id, interaction.user.name)
        streak_xp = 0
        
        if is_correct:
            # Check streak bonuses
            current_streak = user['current_streak']
            for streak_req, bonus in sorted(STREAK_BONUS.items()):
                if current_streak + 1 >= streak_req:
                    streak_xp = bonus
        
        total_xp = (base_xp + time_bonus + streak_xp) if is_correct else 0
        
        # Update database
        stats = await self.db.update_user_stats(interaction.user.id, total_xp, is_correct)
        await self.db.add_quiz_history(
            interaction.user.id,
            self.language,
            self.difficulty,
            self.original_word,
            self.correct_word,
            self.children[selected_index].label,
            is_correct,
            total_xp
        )
        
        # Check achievements
        user_stats = await self.db.get_user_stats(interaction.user.id)
        new_achievements = await self.db.check_achievements(interaction.user.id, user_stats)
        
        # Disable all buttons and colorize
        for item in self.children:
            item.disabled = True
            if int(item.custom_id) == self.correct_index:
                item.style = discord.ButtonStyle.success
            elif int(item.custom_id) == selected_index and not is_correct:
                item.style = discord.ButtonStyle.danger
        
        # Build response
        if is_correct:
            title = "✅ Correct!"
            color = 0x2ecc71
            description = f"**'{self.original_word}'** = **{self.correct_word}**\n\n"
            description += f"💰 **+{total_xp} XP**"
            
            if time_bonus > 0:
                description += f" (⚡ +{time_bonus} speed bonus)"
            if streak_xp > 0:
                description += f"\n🔥 **Streak Bonus: +{streak_xp} XP** ({stats['new_streak']} in a row!)"
        else:
            title = "❌ Incorrect!"
            color = 0xe74c3c
            description = f"The correct answer was: **{self.correct_word}**\n\n"
            description += f"💔 Streak reset: {user['current_streak']} → 0"
        
        # Level up notification
        if stats['level_up']:
            description += f"\n\n🎉 **LEVEL UP!** {stats['old_level']} → {stats['new_level']}"
        
        # Achievement notifications
        if new_achievements:
            description += f"\n\n🏅 **New Achievement{'s' if len(new_achievements) > 1 else ''}:**\n"
            description += "\n".join(new_achievements)
        
        # Progress bar
        current_level, next_level_xp, xp_needed = get_xp_for_next_level(stats['new_xp'])
        if xp_needed:
            description += f"\n\n📊 **{xp_needed} XP** to Level {current_level + 1}"
        
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=f"Total XP: {stats['new_xp']} | Level: {stats['new_level']}")
        
        # In multiplayer, track participant
        if self.is_multiplayer:
            self.game_data['participants'][interaction.user.id] = {
                'is_correct': is_correct,
                'time': time_taken
            }
        
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    await bot.add_cog(Quiz(bot))
