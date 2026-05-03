import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "default_search": "ytsearch",
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

import asyncio
from asyncio import run_coroutine_threadsafe
from urllib import parse, request
import re
import json
import os

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    def play_track(self, voice_client, track):
        source = discord.FFmpegPCMAudio(track["url"], **FFMPEG_OPTIONS)
        source = discord.PCMVolumeTransformer(source, volume=0.5)

        voice_client.play(
            source,
            after=lambda error: self.play_next(voice_client)
        )

    def play_next(self, voice_client):
        if len(self.queue) == 0:
            return
        
        next_track = self.queue.pop(0)
        self.play_track(voice_client, next_track)



    @app_commands.command(name="play", description="Play audio from YouTube or a search query")
    @app_commands.describe(query="YouTube URL, Spotify/Apple Music/Last.fm, or song search")
    async def play(self, interaction: discord.Interaction, query: str):
        if interaction.user.voice is None:
            await interaction.response.send_message(
                "You are not in a voice channel... who will I play music to,,,?",
                ephemeral=True
            )
            return
        await interaction.response.defer()

        channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            voice_client = await channel.connect()
        elif voice_client.channel != channel:
            await voice_client.move_to(channel)

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(query, download=False)

            if "entries" in info:
                info = info["entries"][0]

            audio_url = info["url"]
            title = info.get("title", "Unknown title")
            webpage_url = info.get("webpage_url", query)

        track = {
            "title": title,
            "url": audio_url,
            "webpage_url": webpage_url
        }

        if voice_client.is_playing() or voice_client.is_paused():
            self.queue.append(track)

            embed = discord.Embed(
                title="Added to queue",
                description=f"[{title}]({webpage_url})",
                colour=discord.Colour.yellow()
            )

            await interaction.followup.send(embed=embed)
            return
        
        self.play_track(voice_client, track)

        embed = discord.Embed(
            title="Now Playing",
            description=f"[{title}]({webpage_url})",
            colour=discord.Colour.yellow()
        )

        await interaction.followup.send(embed=embed)    

    @app_commands.command(name="volume", description="Change the playback volume")
    async def volume(self, interaction: discord.Interaction, volume: int):
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            await interaction.response.send_message("I'm not in a voice channel!", ephemeral=True)
            return
        if voice_client.source is None:
            await interaction.response.send_message("Nothing is playing!", ephemeral=True)
            return
        volume = volume / 100
        volume = max(0.0, min(volume, 1.0))
        voice_client.source.volume = volume
        await interaction.response.send_message(f"Volume is now set to {int(volume * 100)}%")

    @app_commands.command(name="pause", description="Pauses music playback")
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            await interaction.response.send_message("I'm not in a voice channel!", ephemeral=True)
            return
        if voice_client.source is None:
            await interaction.response.send_message("Nothing is playing!", ephemeral=True)
            return
        voice_client.pause()
        await interaction.response.send_message("Music paused.")

    @app_commands.command(name="unpause", description="Unpauses music playback")
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            await interaction.response.send_message("I'm not in a voice channel!", ephemeral=True)
            return
        if voice_client.source is None:
            await interaction.response.send_message("Nothing is playing!", ephemeral=True)
            return
        voice_client.resume()
        await interaction.response.send_message("Music unpaused.")
    
    @app_commands.command(name="skip", description="Skips the current song")
    async def skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            await interaction.response.send_message("I'm not in a voice channel!", ephemeral=True)
            return
        if voice_client.source is None:
            await interaction.response.send_message("Nothing is playing!", ephemeral=True)
            return
        voice_client.stop()
        await interaction.response.send_message("Skipped song.")
        
    @app_commands.command(name="queue", description="Show the current queue")
    @app_commands.describe(
        action="What do you want to do?",
        number="Queue position (for removal)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="list", value="list"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="clear", value="clear"),    
    ])
    async def queue(self, interaction: discord.Interaction, action: app_commands.Choice[str], number: int = None):
        if action.value == "list":
            if len(self.queue) == 0:
                await interaction.response.send_message("The queue is empty.")
                return

            queue_text = ""
            for index, track in enumerate(self.queue, start=1):
                queue_text += f"{index}. {track['title']}\n"

            embed = discord.Embed(
                title="Current Queue",
                description=queue_text,
                colour=discord.Colour.yellow()
        )

            await interaction.response.send_message(embed=embed)
            return
        
        if action.value == "remove":
            if number is None:
                await interaction.response.send_message(
                    "You need to specify a number to remove.",
                    ephemeral=True
                )
                return

            if len(self.queue) == 0:
                await interaction.response.send_message(
                    "The queue is empty.",
                    ephemeral=True
                )
                return

            index = number - 1

            if index < 0 or index >= len(self.queue):
                await interaction.response.send_message(
                    "That queue number doesn't exist.",
                    ephemeral=True
                )
                return

            removed_track = self.queue.pop(index)

            await interaction.response.send_message(
                f"Removed **{removed_track['title']}** from the queue."
            )
            return

        if action.value == "clear":
            self.queue.clear()

            await interaction.response.send_message("Queue cleared.")