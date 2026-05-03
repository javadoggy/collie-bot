#/ping
#/join
#/leave
#/play
#/skip
#/mute
#/unmute
#/pause
#/resume
#/stop
#/queue list
#/queue add
#/queue remove
#/next
#/volume
#    /volume <0-100>
#    /volume [show volume]
#/nowplaying
#/clear
#/shuffle
#/loop
#/seek
#/autoplay
#/disconnect
#/connect
#/chat clear
#/kick
#/ban
#/slow


import discord
import discord.ext
import yt_dlp
from discord.ext import commands
from discord import app_commands
from music_cog import music_cog, YDL_OPTIONS, FFMPEG_OPTIONS

VERSION = "dev 1.0.0"

class Spotto(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(music_cog(self))

        guild = discord.Object(id=1404157467180400761)
        
        self.tree.copy_global_to(guild=GUILD_ID)
        synced = await self.tree.sync(guild=guild)
        
        print(f'Synced{len(synced)} commands to guild {guild.id}')
        
# Read Messages
intents = discord.Intents.default()
intents.message_content = True

# Interact with bot
bot = Spotto(command_prefix='!', intents=intents)

GUILD_ID = discord.Object(id=1404157467180400761)

@bot.tree.command(name="connect", description="Connect to your voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice is None:
        await interaction.response.send_message("You are not in a voice channel.", ephemeral=True)
        return
    channel = interaction.user.voice.channel
    if interaction.guild.voice_client is not None:
        await interaction.guild.voice_client.move_to(channel)
    else:
        await channel.connect()
    await interaction.response.send_message(f"Connected to {channel.name}!")

@bot.tree.command(name="disconnect", description="Disconnect from your voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice is None:
        await interaction.response.send_message("You are not in a voice channel.")
        return
    channel = interaction.user.voice.channel
    if interaction.guild.voice_client is not None:
        await interaction.guild.voice_client.disconnect()
    await interaction.response.send_message(f"Disconnected from {channel.name}.")



@bot.tree.command(name="about", description="Learn about Collie!")
@app_commands.describe(option="What do you want to know?")
@app_commands.choices(option=[
    app_commands.Choice(name="status", value="status"),
    app_commands.Choice(name="info", value="info"),
])
async def about(interaction: discord.Interaction, option: app_commands.Choice[str]):

    if option.value == "status":
        embed = discord.Embed(
            title="Collie Status",
            description=f"Collie is running on {VERSION}",
            colour=discord.Colour.yellow()
        )

        embed.add_field(name="Status", value="Online", inline=True)
        embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
        embed.set_footer(text="Collie")
        
        await interaction.response.send_message(embed=embed)
        
    elif option.value == "info":
        embed = discord.Embed(
            title="About Collie",
            description="I am primarily a music bot!",
            colour=discord.Colour.yellow()
        )

        embed.add_field(name="Prefix", value="!", inline=True)
        embed.add_field(name="Slash Commands", value="Enabled", inline=True)
        embed.set_footer(text="Collie")


        await interaction.response.send_message(embed=embed)

with open('token.txt', 'r') as file:
    token = file.read().strip()
bot.run(token)
