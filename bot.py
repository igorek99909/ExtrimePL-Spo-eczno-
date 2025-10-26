import discord
from discord.ext import commands
import os
from welcome_generator import WelcomeImageGenerator
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.default()
intents.members = True  # Required to detect member joins
intents.message_content = True  # Required for commands

bot = commands.Bot(command_prefix='!', intents=intents)

welcome_generator = WelcomeImageGenerator()


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} servers')
    
    # Set bot activity status - "Listening to players on ExtrimePL"
    activity = discord.Activity(
        type=discord.ActivityType.listening,
        name="graczy na ExtrimePL"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    print('Welcome bot is ready to greet new members!')
    print('Bot status set to: Słucha graczy na ExtrimePL')


@bot.event
async def on_member_join(member):
    """Handle new member join event"""
    guild = member.guild

    # Find a channel to send welcome message
    welcome_channel = None

    # Look for channels with "welcome" or "general" in the name
    for channel in guild.text_channels:
        if any(keyword in channel.name.lower()
               for keyword in ['welcome', 'witamy', 'general', 'główny']):
            welcome_channel = channel
            break

    # If no specific welcome channel found, use the first available text channel
    if not welcome_channel:
        welcome_channel = guild.text_channels[
            0] if guild.text_channels else None

    if welcome_channel:
        try:
            # Generate welcome image
            image_path = await welcome_generator.create_welcome_image(
                username=member.display_name,
                member_count=guild.member_count,
                guild_name=guild.name)

            # Create welcome message
            welcome_text = f"Witamy {member.mention}!\n\nUdaj się na kanał weryfikacji aby dokonać weryfikacji konta.\nMamy nadzieję, że zostaniesz na dłużej!\n\nJesteś {guild.member_count}. osobą na serwerze!"

            # Send welcome message with image
            with open(image_path, 'rb') as f:
                picture = discord.File(f)
                await welcome_channel.send(content=member.mention,
                                           file=picture)

            # Clean up temporary image
            os.remove(image_path)

        except Exception as e:
            print(f"Error sending welcome message: {e}")
            # Send text-only welcome message as fallback
            fallback_text = f"Witamy {member.mention} na serwerze {guild.name}! Jesteś {guild.member_count}. osobą na serwerze!"
            await welcome_channel.send(fallback_text)


@bot.command(name='test_welcome')
@commands.has_permissions(administrator=True)
async def test_welcome(ctx):
    """Test command to preview welcome message"""
    try:
        # Generate test welcome image
        image_path = await welcome_generator.create_welcome_image(
            username=ctx.author.display_name,
            member_count=ctx.guild.member_count,
            guild_name=ctx.guild.name)

        # Send test welcome message
        test_text = f"Test wiadomości powitalnej dla {ctx.author.mention}!"

        with open(image_path, 'rb') as f:
            picture = discord.File(f)
            await ctx.send(content=test_text, file=picture)

        # Clean up temporary image
        os.remove(image_path)

    except Exception as e:
        await ctx.send(f"Błąd podczas generowania wiadomości powitalnej: {e}")


if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("Error: DISCORD_BOT_TOKEN environment variable not set!")
        print("Please set your Discord bot token in the secrets.")
        exit(1)

    bot.run(token)
