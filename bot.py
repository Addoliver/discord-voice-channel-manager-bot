import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Store voice channel data
voice_channels = {}

class VoiceChannel:
    def __init__(self, channel, owner):
        self.channel = channel
        self.owner = owner
        self.guests = set()
        self.blacklist = set()
        self.whitelist = set()
        self.is_private = False
        self.host = owner  # Current host (can be different from owner)

class ChannelSizeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Buttons don't timeout
        
        # Define size options with their visual styles
        sizes = [
            ("Duo", "2", "🎮", discord.ButtonStyle.blurple),
            ("Trio", "3", "🎲", discord.ButtonStyle.green),
            ("Quad", "4", "🎯", discord.ButtonStyle.blurple),
            ("Penta", "5", "🎪", discord.ButtonStyle.red),
            ("Hexa", "6", "🎨", discord.ButtonStyle.blurple),
            ("Septa", "7", "🎭", discord.ButtonStyle.green),
            ("Octa", "8", "🎼", discord.ButtonStyle.blurple),
            ("Deca", "10", "🎬", discord.ButtonStyle.red),
            ("Unlimited", "0", "♾️", discord.ButtonStyle.blurple),
            ("Custom", "custom", "⚙️", discord.ButtonStyle.gray)
        ]
        
        # Add buttons to the view
        for label, size, emoji, style in sizes:
            self.add_item(ChannelSizeButton(label, size, emoji, style))

class ChannelSizeButton(discord.ui.Button):
    def __init__(self, label, size, emoji, style):
        super().__init__(
            label=f"{label}" if size in ["0", "custom"] else f"{label} ({size})",
            emoji=emoji,
            style=style,
            custom_id=f"size_{size}"
        )
        self.size = size

    async def callback(self, interaction: discord.Interaction):
        if self.size == "custom":
            embed = discord.Embed(
                title="⚙️ Custom Size Channel",
                description=(
                    "To create a custom size channel, use the command:\n"
                    "`!size <number>` - Set any size between 1 and 99"
                ),
                color=discord.Color.yellow()
            )
            embed.set_footer(text="Example: !size 15")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        try:
            size = int(self.size)
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(connect=True),
                interaction.user: discord.PermissionOverwrite(connect=True, manage_channels=True)
            }
            
            # Get or create voice category
            voice_category = discord.utils.get(interaction.guild.categories, name="Voice Channels")
            if not voice_category:
                voice_category = await interaction.guild.create_category("Voice Channels")
            
            # Create the channel
            channel = await interaction.guild.create_voice_channel(
                name=f"{interaction.user.name}'s Channel",
                category=voice_category,
                user_limit=size if size > 0 else None,
                overwrites=overwrites
            )
            
            # Store channel data
            voice_channels[channel.id] = VoiceChannel(channel, interaction.user)
            
            # Move user if they're in a voice channel
            if interaction.user.voice:
                await interaction.user.move_to(channel)
            
            # Create success embed
            embed = discord.Embed(
                title="🎮 Channel Created",
                description=(
                    f"Your voice channel has been created with "
                    f"{'unlimited' if size == 0 else str(size)} slots!"
                ),
                color=discord.Color.green()
            )
            embed.add_field(
                name="📋 Channel Info",
                value=(
                    f"**Name:** {channel.name}\n"
                    f"**Size:** {'Unlimited' if size == 0 else f'{size} members'}\n"
                    f"**Owner:** {interaction.user.name}"
                ),
                inline=False
            )
            embed.add_field(
                name="🛠️ Available Commands",
                value=(
                    "• `!name <new_name>` - Rename channel\n"
                    "• `!privacy` - Toggle private mode\n"
                    "• `!size <number>` - Change size\n"
                    "• `!help` - View all commands"
                ),
                inline=False
            )
            embed.set_footer(text="Anti Stress Voice Channels • Type !commands for more options")
            
            # Send to log channel if exists
            log_channel = discord.utils.get(interaction.guild.text_channels, name="voice-logs")
            if log_channel:
                log_embed = discord.Embed(
                    title="🎮 Voice Channel Created",
                    description=f"{interaction.user.name} created a new voice channel",
                    color=discord.Color.green()
                )
                log_embed.add_field(name="Channel Name", value=channel.name)
                log_embed.add_field(name="Size", value=f"{'Unlimited' if size == 0 else str(size)} slots")
                log_embed.add_field(name="Created By", value=interaction.user.name)
                await log_channel.send(embed=log_embed)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to create channel: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

async def create_info_embed():
    """Create the voice channel information embed"""
    embed = discord.Embed(
        title="🎮 Anti Stress Voice Channels",
        description=(
            "Create your own custom voice channel with advanced features and full control! "
            "Choose from preset sizes or create a custom-sized channel."
        ),
        color=discord.Color.blue()
    )
    
    # Channel Features
    embed.add_field(
        name="✨ Channel Features",
        value=(
            "• 🔒 Private or Public mode\n"
            "• 👥 Custom member limit\n"
            "• 📝 Custom channel name\n"
            "• 🎵 Adjustable bitrate\n"
            "• ⚡ Quick size presets"
        ),
        inline=True
    )
    
    # Management Features
    embed.add_field(
        name="🛠️ Management",
        value=(
            "• 👑 Full owner controls\n"
            "• ✅ Whitelist system\n"
            "• ❌ Blacklist system\n"
            "• 🎯 Temporary hosts\n"
            "• 🔄 Auto-cleanup"
        ),
        inline=True
    )
    
    # Size Presets
    embed.add_field(
        name="📊 Available Sizes",
        value=(
            "**Quick Create Buttons:**\n"
            "• 🎮 Duo (2) • 🎲 Trio (3)\n"
            "• 🎯 Quad (4) • 🎪 Penta (5)\n"
            "• 🎨 Hexa (6) • 🎭 Septa (7)\n"
            "• 🎼 Octa (8) • 🎬 Deca (10)\n"
            "• ♾️ Unlimited • ⚙️ Custom"
        ),
        inline=False
    )
    
    # Important Notes
    embed.add_field(
        name="📝 Important Notes",
        value=(
            "• Channels auto-delete when empty\n"
            "• Staff can access any channel if needed\n"
            "• All server rules apply in custom channels\n"
            "• Use `!commands` for full command list\n"
            "• Click buttons below to create a channel"
        ),
        inline=False
    )
    
    embed.set_footer(text="Anti Stress Voice Channels • Click a button below to create your channel")
    return embed

import asyncio

import os

GUILD_ID = int(os.getenv('GUILD_ID', '0'))

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    # Start background task to cycle activities
    bot.loop.create_task(cycle_activities())

    # Create initial voice channel if it doesn't exist
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    if guild:
        # Create voice category
        voice_category = discord.utils.get(guild.categories, name="・ PRIVATE VOICE ZONE・")
        if not voice_category:
            voice_category = await guild.create_category("・ PRIVATE VOICE ZONE・")
        
        # Create join channel
        join_channel = discord.utils.get(guild.voice_channels, name="private¹")
        if not join_channel:
            join_channel = await guild.create_voice_channel(
                name="private¹",
                category=voice_category
            )
        
        # Post info in the designated info channel
        info_channel_id = os.getenv('INFO_CHANNEL_ID')
        if info_channel_id:
            try:
                info_channel = await bot.fetch_channel(int(info_channel_id))
                # Send new info embed
                await info_channel.send(embed=await create_info_embed(), view=ChannelSizeView())
            except Exception as e:
                print(f"Error posting to info channel: {str(e)}")

async def cycle_activities():
    while True:
        guild = discord.utils.get(bot.guilds, id=GUILD_ID)
        if guild:
            total_members = guild.member_count
        else:
            total_members = 0
        
        activities = [
            discord.Game(name=f"Hug {total_members} members!"),
            discord.Game(name="Powered by custom-vcs"),
            discord.Game(name="Owner: Oliver_Ol")
        ]
        
        for activity in activities:
            await bot.change_presence(activity=activity)
            await asyncio.sleep(10)  # Display each activity for 10 seconds

@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice channel join/leave events"""
    if member.guild.id != GUILD_ID:
        return

    # Get or create log channel
    log_channel = discord.utils.get(member.guild.text_channels, name="voice-logs")
    if not log_channel:
        try:
            log_channel = await member.guild.create_text_channel("voice-logs")
        except:
            log_channel = None

    # When a user joins the "Join to Create" channel
    if after.channel and after.channel.name == "➕ Join to Create":
        # Create a new voice channel for the user
        category = after.channel.category
        new_channel = await member.guild.create_voice_channel(
            name=f"{member.name}'s Channel",
            category=category
        )
        # Move the user to their new channel
        await member.move_to(new_channel)
        # Store the channel data
        voice_channels[new_channel.id] = VoiceChannel(new_channel, member)
        
        # Log channel creation
        if log_channel:
            embed = discord.Embed(
                title="Voice Channel Created",
                description=f"{member.name} created a new voice channel",
                color=discord.Color.green()
            )
            embed.add_field(name="Channel Name", value=new_channel.name)
            embed.add_field(name="Created By", value=member.name)
            await log_channel.send(embed=embed)
        
    # When a user joins any voice channel
    elif after.channel and after.channel != before.channel:
        if log_channel:
            embed = discord.Embed(
                title="User Joined Voice",
                description=f"{member.name} joined a voice channel",
                color=discord.Color.blue()
            )
            embed.add_field(name="Channel", value=after.channel.name)
            await log_channel.send(embed=embed)
    
    # When a user leaves a voice channel
    if before.channel:
        if before.channel.id in voice_channels:
            # If the channel is empty and it's not the "Join to Create" channel
            if len(before.channel.members) == 0 and before.channel.name != "➕ Join to Create":
                # Log channel deletion
                if log_channel:
                    embed = discord.Embed(
                        title="Voice Channel Deleted",
                        description=f"Empty channel was automatically deleted",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Channel Name", value=before.channel.name)
                    await log_channel.send(embed=embed)
                
                # Delete the channel
                await before.channel.delete()
                # Remove the channel data
                del voice_channels[before.channel.id]
        
        # Log user leaving
        elif log_channel and not after.channel:
            embed = discord.Embed(
                title="User Left Voice",
                description=f"{member.name} left the voice channel",
                color=discord.Color.orange()
            )
            embed.add_field(name="Channel", value=before.channel.name)
            await log_channel.send(embed=embed)

# Channel Management Commands
def guild_only():
    def predicate(ctx):
        return ctx.guild and ctx.guild.id == GUILD_ID
    return commands.check(predicate)

@bot.command(name='create')
@guild_only()
async def create_voice(ctx, name: str, size: int = 0):
    """Create a new voice channel"""
    try:
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(connect=True),
            ctx.author: discord.PermissionOverwrite(connect=True, manage_channels=True)
        }
        
        channel = await ctx.guild.create_voice_channel(
            name,
            user_limit=size if size > 0 else None,
            overwrites=overwrites
        )
        
        voice_channels[channel.id] = VoiceChannel(channel, ctx.author)
        
        # Create success embed
        embed = discord.Embed(
            title="Voice Channel Created",
            description=f'Voice channel "{name}" created successfully!',
            color=discord.Color.green()
        )
        embed.add_field(name="Channel Name", value=name)
        embed.add_field(name="Size", value=f"{size} people" if size > 0 else "Unlimited")
        embed.add_field(name="Owner", value=ctx.author.name)
        
        # Send to log channel if exists
        log_channel = discord.utils.get(ctx.guild.text_channels, name="voice-logs")
        if log_channel:
            await log_channel.send(embed=embed)
            
        await ctx.send(embed=embed)
    except Exception as e:
        error_embed = discord.Embed(
            title="Error",
            description=f'Error creating channel: {str(e)}',
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

@bot.command(name='privacy')
async def toggle_privacy(ctx):
    """Toggle channel privacy"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        error_embed = discord.Embed(
            title="Error",
            description="You must be in your custom voice channel!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner:
        error_embed = discord.Embed(
            title="Error",
            description="Only the channel owner can change privacy settings!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
        
    channel_data.is_private = not channel_data.is_private
    status = "private" if channel_data.is_private else "public"
    
    # Create success embed
    embed = discord.Embed(
        title="Privacy Updated",
        description=f"Channel is now {status}",
        color=discord.Color.green()
    )
    embed.add_field(name="Channel", value=channel_data.channel.name)
    embed.add_field(name="Status", value=status.capitalize())
    embed.add_field(name="Owner", value=ctx.author.name)
    
    # Send to log channel if exists
    log_channel = discord.utils.get(ctx.guild.text_channels, name="voice-logs")
    if log_channel:
        await log_channel.send(embed=embed)
        
    await ctx.send(embed=embed)

@bot.command(name='whitelist')
async def whitelist_user(ctx, member: discord.Member):
    """Add a user to the whitelist"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        error_embed = discord.Embed(
            title="Error",
            description="You must be in your custom voice channel!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner:
        error_embed = discord.Embed(
            title="Error",
            description="Only the channel owner can modify the whitelist!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
        
    channel_data.whitelist.add(member.id)
    
    # Create success embed
    embed = discord.Embed(
        title="User Whitelisted",
        description=f"{member.name} has been added to the whitelist",
        color=discord.Color.green()
    )
    embed.add_field(name="Channel", value=channel_data.channel.name)
    embed.add_field(name="Whitelisted User", value=member.name)
    embed.add_field(name="Owner", value=ctx.author.name)
    
    # Send to log channel if exists
    log_channel = discord.utils.get(ctx.guild.text_channels, name="voice-logs")
    if log_channel:
        log_embed = discord.Embed(
            title="Whitelist Updated",
            description=f"A user was added to channel whitelist",
            color=discord.Color.blue()
        )
        log_embed.add_field(name="Channel", value=channel_data.channel.name)
        log_embed.add_field(name="Added User", value=member.name)
        log_embed.add_field(name="Added By", value=ctx.author.name)
        await log_channel.send(embed=log_embed)
        
    await ctx.send(embed=embed)

@bot.command(name='blacklist')
async def blacklist_user(ctx, member: discord.Member):
    """Add a user to the blacklist"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        error_embed = discord.Embed(
            title="Error",
            description="You must be in your custom voice channel!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner:
        error_embed = discord.Embed(
            title="Error",
            description="Only the channel owner can modify the blacklist!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
        
    channel_data.blacklist.add(member.id)
    if member.voice and member.voice.channel == channel_data.channel:
        await member.move_to(None)  # Disconnect the user if they're in the channel
    
    # Create success embed
    embed = discord.Embed(
        title="User Blacklisted",
        description=f"{member.name} has been added to the blacklist",
        color=discord.Color.green()
    )
    embed.add_field(name="Channel", value=channel_data.channel.name)
    embed.add_field(name="Blacklisted User", value=member.name)
    embed.add_field(name="Owner", value=ctx.author.name)
    
    # Send to log channel if exists
    log_channel = discord.utils.get(ctx.guild.text_channels, name="voice-logs")
    if log_channel:
        log_embed = discord.Embed(
            title="Blacklist Updated",
            description=f"A user was added to channel blacklist",
            color=discord.Color.red()
        )
        log_embed.add_field(name="Channel", value=channel_data.channel.name)
        log_embed.add_field(name="Blacklisted User", value=member.name)
        log_embed.add_field(name="Added By", value=ctx.author.name)
        if member.voice and member.voice.channel == channel_data.channel:
            log_embed.add_field(name="Action", value="User was disconnected from the channel")
        await log_channel.send(embed=log_embed)
        
    await ctx.send(embed=embed)

@bot.command(name='info')
async def channel_info(ctx):
    """Display channel information"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        error_embed = discord.Embed(
            title="Error",
            description="You must be in a custom voice channel!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    channel = channel_data.channel
    
    info = discord.Embed(
        title=f"Channel Information: {channel.name}",
        color=discord.Color.blue()
    )
    
    # Basic Information
    info.add_field(name="Owner", value=channel_data.owner.name, inline=True)
    info.add_field(name="Current Host", value=channel_data.host.name, inline=True)
    info.add_field(name="Privacy", value="Private" if channel_data.is_private else "Public", inline=True)
    
    # Channel Settings
    info.add_field(name="User Limit", value=channel.user_limit or "Unlimited", inline=True)
    info.add_field(name="Bitrate", value=f"{channel.bitrate//1000}kbps", inline=True)
    info.add_field(name="Current Users", value=len(channel.members), inline=True)
    
    # Current Members
    members_list = "\n".join([member.name for member in channel.members]) or "None"
    info.add_field(name="Current Members", value=members_list, inline=False)
    
    # Whitelist/Blacklist
    if channel_data.whitelist:
        whitelist = "\n".join([ctx.guild.get_member(user_id).name for user_id in channel_data.whitelist if ctx.guild.get_member(user_id)]) or "None"
        info.add_field(name="Whitelisted Users", value=whitelist, inline=True)
    
    if channel_data.blacklist:
        blacklist = "\n".join([ctx.guild.get_member(user_id).name for user_id in channel_data.blacklist if ctx.guild.get_member(user_id)]) or "None"
        info.add_field(name="Blacklisted Users", value=blacklist, inline=True)
    
    # Guest List
    if channel_data.guests:
        guests = "\n".join([ctx.guild.get_member(user_id).name for user_id in channel_data.guests if ctx.guild.get_member(user_id)]) or "None"
        info.add_field(name="Guest List", value=guests, inline=False)
    
    info.set_footer(text="Use !commands to see available channel management commands")
    
    # Send to log channel if exists
    log_channel = discord.utils.get(ctx.guild.text_channels, name="voice-logs")
    if log_channel:
        log_embed = discord.Embed(
            title="Channel Info Requested",
            description=f"Channel information was viewed",
            color=discord.Color.blue()
        )
        log_embed.add_field(name="Channel", value=channel.name)
        log_embed.add_field(name="Requested By", value=ctx.author.name)
        await log_channel.send(embed=log_embed)
    
    await ctx.send(embed=info)

@bot.command(name='size')
async def set_size(ctx, limit: int):
    """Set the channel size limit"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        error_embed = discord.Embed(
            title="Error",
            description="You must be in your custom voice channel!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner:
        error_embed = discord.Embed(
            title="Error",
            description="Only the channel owner can change the size limit!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
    
    try:
        old_limit = channel_data.channel.user_limit or "Unlimited"
        await channel_data.channel.edit(user_limit=limit if limit > 0 else None)
        
        # Create success embed
        embed = discord.Embed(
            title="Channel Size Updated",
            description=f"Channel size limit has been updated",
            color=discord.Color.green()
        )
        embed.add_field(name="Channel", value=channel_data.channel.name)
        embed.add_field(name="New Size", value=f"{limit} people" if limit > 0 else "Unlimited")
        embed.add_field(name="Previous Size", value=f"{old_limit}")
        
        # Send to log channel if exists
        log_channel = discord.utils.get(ctx.guild.text_channels, name="voice-logs")
        if log_channel:
            log_embed = discord.Embed(
                title="Channel Size Changed",
                description=f"Voice channel size was modified",
                color=discord.Color.blue()
            )
            log_embed.add_field(name="Channel", value=channel_data.channel.name)
            log_embed.add_field(name="Changed By", value=ctx.author.name)
            log_embed.add_field(name="Old Size", value=f"{old_limit}")
            log_embed.add_field(name="New Size", value=f"{limit} people" if limit > 0 else "Unlimited")
            await log_channel.send(embed=log_embed)
            
        await ctx.send(embed=embed)
    except discord.errors.InvalidArgument:
        error_embed = discord.Embed(
            title="Error",
            description="Invalid size limit! Must be between 0 (unlimited) and 99.",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

@bot.command(name='name')
async def change_name(ctx, *, new_name: str):
    """Change the channel name"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        error_embed = discord.Embed(
            title="Error",
            description="You must be in your custom voice channel!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner:
        error_embed = discord.Embed(
            title="Error",
            description="Only the channel owner can change the channel name!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
    
    try:
        old_name = channel_data.channel.name
        await channel_data.channel.edit(name=new_name)
        
        # Create success embed
        embed = discord.Embed(
            title="Channel Name Updated",
            description=f"Channel name has been changed successfully",
            color=discord.Color.green()
        )
        embed.add_field(name="New Name", value=new_name)
        embed.add_field(name="Previous Name", value=old_name)
        embed.add_field(name="Changed By", value=ctx.author.name)
        
        # Send to log channel if exists
        log_channel = discord.utils.get(ctx.guild.text_channels, name="voice-logs")
        if log_channel:
            log_embed = discord.Embed(
                title="Channel Name Changed",
                description=f"Voice channel name was modified",
                color=discord.Color.blue()
            )
            log_embed.add_field(name="Old Name", value=old_name)
            log_embed.add_field(name="New Name", value=new_name)
            log_embed.add_field(name="Changed By", value=ctx.author.name)
            await log_channel.send(embed=log_embed)
            
        await ctx.send(embed=embed)
    except discord.errors.InvalidArgument:
        error_embed = discord.Embed(
            title="Error",
            description="Invalid channel name! The name must be between 1 and 100 characters.",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

@bot.command(name='guests')
async def manage_guests(ctx, action: str, member: discord.Member = None):
    """Manage guest list for the channel"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        error_embed = discord.Embed(
            title="Error",
            description="You must be in your custom voice channel!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner and ctx.author != channel_data.host:
        error_embed = discord.Embed(
            title="Error",
            description="Only the channel owner or host can manage guests!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return

    try:
        if action.lower() == "add" and member:
            channel_data.guests.add(member.id)
            embed = discord.Embed(
                title="Guest Added",
                description=f"{member.name} has been added to the guest list",
                color=discord.Color.green()
            )
            embed.add_field(name="Channel", value=channel_data.channel.name)
            embed.add_field(name="Guest", value=member.name)
            embed.add_field(name="Added By", value=ctx.author.name)
            
            # Log the action
            log_channel = discord.utils.get(ctx.guild.text_channels, name="voice-logs")
            if log_channel:
                log_embed = discord.Embed(
                    title="Guest List Updated",
                    description=f"A new guest was added",
                    color=discord.Color.blue()
                )
                log_embed.add_field(name="Channel", value=channel_data.channel.name)
                log_embed.add_field(name="Guest Added", value=member.name)
                log_embed.add_field(name="Added By", value=ctx.author.name)
                await log_channel.send(embed=log_embed)
                
        elif action.lower() == "remove" and member:
            channel_data.guests.remove(member.id)
            embed = discord.Embed(
                title="Guest Removed",
                description=f"{member.name} has been removed from the guest list",
                color=discord.Color.orange()
            )
            embed.add_field(name="Channel", value=channel_data.channel.name)
            embed.add_field(name="Guest", value=member.name)
            embed.add_field(name="Removed By", value=ctx.author.name)
            
            # Log the action
            log_channel = discord.utils.get(ctx.guild.text_channels, name="voice-logs")
            if log_channel:
                log_embed = discord.Embed(
                    title="Guest List Updated",
                    description=f"A guest was removed",
                    color=discord.Color.blue()
                )
                log_embed.add_field(name="Channel", value=channel_data.channel.name)
                log_embed.add_field(name="Guest Removed", value=member.name)
                log_embed.add_field(name="Removed By", value=ctx.author.name)
                await log_channel.send(embed=log_embed)
                
        elif action.lower() == "list":
            guest_list = [ctx.guild.get_member(guest_id).name for guest_id in channel_data.guests if ctx.guild.get_member(guest_id)]
            embed = discord.Embed(
                title="Guest List",
                description=f"Current guests for {channel_data.channel.name}",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Guests",
                value="\n".join(guest_list) if guest_list else "No guests",
                inline=False
            )
            embed.set_footer(text="Use !guests add/remove <user> to modify the list")
        else:
            embed = discord.Embed(
                title="Error",
                description="Invalid action! Use 'add', 'remove', or 'list'",
                color=discord.Color.red()
            )
            
        await ctx.send(embed=embed)
    except Exception as e:
        error_embed = discord.Embed(
            title="Error",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

@bot.command(name='host')
async def set_host(ctx, member: discord.Member):
    """Set a temporary host for the channel"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        error_embed = discord.Embed(
            title="Error",
            description="You must be in your custom voice channel!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner:
        error_embed = discord.Embed(
            title="Error",
            description="Only the channel owner can set a host!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
    
    try:
        old_host = channel_data.host
        channel_data.host = member
        
        # Create success embed
        embed = discord.Embed(
            title="Channel Host Updated",
            description=f"Channel host has been changed successfully",
            color=discord.Color.green()
        )
        embed.add_field(name="Channel", value=channel_data.channel.name)
        embed.add_field(name="New Host", value=member.name)
        embed.add_field(name="Previous Host", value=old_host.name)
        
        # Send to log channel if exists
        log_channel = discord.utils.get(ctx.guild.text_channels, name="voice-logs")
        if log_channel:
            log_embed = discord.Embed(
                title="Channel Host Changed",
                description=f"Voice channel host was modified",
                color=discord.Color.blue()
            )
            log_embed.add_field(name="Channel", value=channel_data.channel.name)
            log_embed.add_field(name="Old Host", value=old_host.name)
            log_embed.add_field(name="New Host", value=member.name)
            log_embed.add_field(name="Changed By", value=ctx.author.name)
            await log_channel.send(embed=log_embed)
            
        await ctx.send(embed=embed)
    except Exception as e:
        error_embed = discord.Embed(
            title="Error",
            description=f"Failed to set host: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

@bot.command(name='view')
async def view_channel(ctx):
    """View channel settings and information"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        error_embed = discord.Embed(
            title="❌ Error",
            description="You must be in a custom voice channel!",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    channel = channel_data.channel
    
    # Create detailed embed
    view = discord.Embed(
        title=f"🎮 Channel View: {channel.name}",
        description="Detailed view of channel settings and status",
        color=discord.Color.blue()
    )
    
    # Basic Information
    view.add_field(
        name="📊 Basic Info",
        value=f"**👑 Owner:** {channel_data.owner.name}\n"
              f"**🎯 Current Host:** {channel_data.host.name}\n"
              f"**🔒 Privacy:** {'Private 🔐' if channel_data.is_private else 'Public 🔓'}\n"
              f"**👥 User Limit:** {channel.user_limit or '∞ Unlimited'}\n"
              f"**🎵 Bitrate:** {channel.bitrate//1000}kbps",
        inline=False
    )
    
    # Current Members
    current_members = "\n".join([f"• {member.name}" for member in channel.members]) or "None"
    view.add_field(
        name=f"👥 Current Members ({len(channel.members)})",
        value=current_members,
        inline=False
    )
    
    # Guest List
    if channel_data.guests:
        guests = "\n".join([f"• {ctx.guild.get_member(guest_id).name}" for guest_id in channel_data.guests if ctx.guild.get_member(guest_id)]) or "None"
        view.add_field(
            name=f"✨ Guest List ({len(channel_data.guests)})",
            value=guests,
            inline=False
        )
    
    # Whitelist/Blacklist
    if channel_data.whitelist:
        whitelist = "\n".join([f"• {ctx.guild.get_member(user_id).name}" for user_id in channel_data.whitelist if ctx.guild.get_member(user_id)]) or "None"
        view.add_field(
            name=f"✅ Whitelist ({len(channel_data.whitelist)})",
            value=whitelist,
            inline=True
        )
    
    if channel_data.blacklist:
        blacklist = "\n".join([f"• {ctx.guild.get_member(user_id).name}" for user_id in channel_data.blacklist if ctx.guild.get_member(user_id)]) or "None"
        view.add_field(
            name=f"❌ Blacklist ({len(channel_data.blacklist)})",
            value=blacklist,
            inline=True
        )
    
    view.set_footer(text="💡 Use !commands to see available management commands")
    
    # Send to log channel if exists
    log_channel = discord.utils.get(ctx.guild.text_channels, name="voice-logs")
    if log_channel:
        log_embed = discord.Embed(
            title="👁️ Channel Info Viewed",
            description=f"Channel information was requested",
            color=discord.Color.blue()
        )
        log_embed.add_field(name="Channel", value=channel.name)
        log_embed.add_field(name="Viewed By", value=ctx.author.name)
        await log_channel.send(embed=log_embed)
    
    await ctx.send(embed=view)

@bot.command(name='changehost')
async def change_host(ctx, member: discord.Member):
    """Change the channel host"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        await ctx.send("You must be in your custom voice channel!")
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner:
        await ctx.send("Only the channel owner can change the host!")
        return
        
    channel_data.host = member
    await ctx.send(f"{member.name} is now the channel host!")

@bot.command(name='mute')
async def mute_user(ctx, member: discord.Member):
    """Mute a user in the channel"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        await ctx.send("You must be in your custom voice channel!")
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner and ctx.author != channel_data.host:
        await ctx.send("Only the channel owner or host can mute users!")
        return
        
    await member.edit(mute=True)
    await ctx.send(f"{member.name} has been muted!")

@bot.command(name='unmute')
async def unmute_user(ctx, member: discord.Member):
    """Unmute a user in the channel"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        await ctx.send("You must be in your custom voice channel!")
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner and ctx.author != channel_data.host:
        await ctx.send("Only the channel owner or host can unmute users!")
        return
        
    await member.edit(mute=False)
    await ctx.send(f"{member.name} has been unmuted!")

@bot.command(name='ban')
async def ban_user(ctx, member: discord.Member):
    """Ban a user from the channel"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        await ctx.send("You must be in your custom voice channel!")
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner:
        await ctx.send("Only the channel owner can ban users!")
        return
        
    await channel_data.channel.set_permissions(member, connect=False)
    if member.voice and member.voice.channel == channel_data.channel:
        await member.move_to(None)
    await ctx.send(f"{member.name} has been banned from the channel!")

@bot.command(name='unban')
async def unban_user(ctx, member: discord.Member):
    """Unban a user from the channel"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        await ctx.send("You must be in your custom voice channel!")
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner:
        await ctx.send("Only the channel owner can unban users!")
        return
        
    await channel_data.channel.set_permissions(member, connect=True)
    await ctx.send(f"{member.name} has been unbanned from the channel!")

@bot.command(name='reset')
async def reset_channel(ctx):
    """Reset channel settings to default"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        await ctx.send("You must be in your custom voice channel!")
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner:
        await ctx.send("Only the channel owner can reset the channel!")
        return
        
    # Reset channel settings
    channel_data.is_private = False
    channel_data.guests.clear()
    channel_data.blacklist.clear()
    channel_data.whitelist.clear()
    channel_data.host = channel_data.owner
    
    # Reset channel permissions
    await channel_data.channel.edit(
        name=f"{ctx.author.name}'s Channel",
        user_limit=None,
        bitrate=64000
    )
    
    # Reset all user-specific permissions
    for overwrite in channel_data.channel.overwrites:
        if isinstance(overwrite, discord.Member) and overwrite != ctx.author:
            await channel_data.channel.set_permissions(overwrite, overwrite=None)
            
    await ctx.send("Channel has been reset to default settings!")

@bot.command(name='transfer')
async def transfer_ownership(ctx, new_owner: discord.Member):
    """Transfer channel ownership to another user"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        await ctx.send("You must be in your custom voice channel!")
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner:
        await ctx.send("Only the channel owner can transfer ownership!")
        return
        
    # Update permissions
    await channel_data.channel.set_permissions(ctx.author, connect=True)
    await channel_data.channel.set_permissions(new_owner, connect=True, manage_channels=True)
    
    # Update channel data
    channel_data.owner = new_owner
    channel_data.host = new_owner
    
    await ctx.send(f"Channel ownership has been transferred to {new_owner.name}!")

@bot.command(name='bitrate')
async def set_bitrate(ctx, bitrate: int):
    """Set the channel bitrate (in kbps)"""
    if not ctx.author.voice or ctx.author.voice.channel.id not in voice_channels:
        await ctx.send("You must be in your custom voice channel!")
        return
        
    channel_data = voice_channels[ctx.author.voice.channel.id]
    if ctx.author != channel_data.owner:
        await ctx.send("Only the channel owner can change the bitrate!")
        return
        
    try:
        # Convert kbps to bps
        await channel_data.channel.edit(bitrate=bitrate * 1000)
        await ctx.send(f"Channel bitrate set to {bitrate}kbps!")
    except discord.errors.InvalidArgument:
        await ctx.send("Invalid bitrate! Must be between 8 and 96 kbps for most servers.")


@bot.command(name='helpvc')
async def help_command(ctx):
    """Show help information"""
    help_channel_id = os.getenv('HELP_CHANNEL_ID')
    if not help_channel_id:
        error_embed = discord.Embed(
            title="❌ Error",
            description="Help channel not configured. Please contact an administrator.",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return

    try:
        help_channel = await bot.fetch_channel(int(help_channel_id))
        
        # Create help embed
        embed = discord.Embed(
            title="🎮 Voice Channel Help",
            description=(
                "Welcome to Anti Stress Voice Channels! Here's your quick guide to "
                "essential features and commands."
            ),
            color=discord.Color.blue()
        )
        
        # Core Commands
        embed.add_field(
            name="📋 Basic Commands",
            value=(
                "• `!create <name> [size]` Create a channel\n"
                "• `!name <new_name>` Rename channel\n"
                "• `!size <number>` Set member limit\n"
                "• `!privacy` Toggle private mode\n"
                "• `!info` View channel details"
            ),
            inline=False
        )
        
        # Management
        embed.add_field(
            name="⚙️ Management",
            value=(
                "• `!whitelist <user>` Allow specific users\n"
                "• `!blacklist <user>` Block specific users\n"
                "• `!guests add/remove <user>` Manage guests\n"
                "• `!host <user>` Set temporary host\n"
                "• `!transfer <user>` Transfer ownership"
            ),
            inline=False
        )
        
        # Quick Tips
        embed.add_field(
            name="💡 Quick Tips",
            value=(
                "• Use quick-create buttons below info panel\n"
                "• Private channels are invite-only\n"
                "• Temporary hosts can manage users\n"
                "• Channels auto-delete when empty\n"
                "• Type `!commands` for full command list"
            ),
            inline=False
        )
        
        embed.set_footer(text="Anti Stress Voice Channels • Type !helpvc for quick help or !commands for detailed list")

        # Send new help embed
        await help_channel.send(embed=embed)
        
        # Send confirmation to user
        confirm_embed = discord.Embed(
            title="✅ Help Updated",
            description=f"Help information has been posted in <#{help_channel_id}>",
            color=discord.Color.green()
        )
        await ctx.send(embed=confirm_embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to update help channel: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

@bot.command(name='commands')
async def show_commands(ctx):
    """Display available commands"""
    help_channel_id = os.getenv('HELP_CHANNEL_ID')
    if not help_channel_id:
        error_embed = discord.Embed(
            title="❌ Error",
            description="Help channel not configured. Please contact an administrator.",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)
        return

    try:
        help_channel = await bot.fetch_channel(int(help_channel_id))
        
        help_embed = discord.Embed(
            title="🎮 Anti Stress Voice Commands",
            description=(
                "Welcome to Anti Stress Voice Channels! Here's your complete guide to all "
                "available commands and features. Commands are organized by category for easy reference."
            ),
            color=discord.Color.blue()
        )

        # Core Channel Management
        help_embed.add_field(
            name="🎯 Core Commands",
            value=(
                "• `!create <name> [size]` Create your own channel\n"
                "• `!info` View channel features and options\n"
                "• `!view` See detailed channel information"
            ),
            inline=False
        )

        # Channel Settings
        help_embed.add_field(
            name="⚙️ Channel Settings",
            value=(
                "• `!name <new_name>` Rename your channel\n"
                "• `!size <limit>` Set member limit (0 for unlimited)\n"
                "• `!bitrate <value>` Adjust audio quality (8-96 kbps)\n"
                "• `!reset` Restore default settings"
            ),
            inline=False
        )

        # Privacy & Security
        help_embed.add_field(
            name="🔒 Privacy & Security",
            value=(
                "• `!privacy` Toggle private/public mode\n"
                "• `!whitelist <user>` Allow specific users\n"
                "• `!blacklist <user>` Block specific users\n"
                "• `!unban <user>` Remove user from blacklist"
            ),
            inline=False
        )

        # User Management
        help_embed.add_field(
            name="👥 User Management",
            value=(
                "• `!guests add <user>` Add to guest list\n"
                "• `!guests remove <user>` Remove from guest list\n"
                "• `!guests list` View current guests\n"
                "• `!mute <user>` Mute a user\n"
                "• `!unmute <user>` Unmute a user"
            ),
            inline=False
        )

        # Administrative
        help_embed.add_field(
            name="👑 Administrative",
            value=(
                "• `!transfer <user>` Transfer channel ownership\n"
                "• `!host <user>` Set temporary host\n"
                "• `!changehost <user>` Change current host"
            ),
            inline=False
        )

        # Pro Tips
        help_embed.add_field(
            name="💡 Pro Tips",
            value=(
                "• Use quick-create buttons below info panel\n"
                "• Private channels are invite-only\n"
                "• Channels auto-delete when empty\n"
                "• Owners can set temporary hosts\n"
                "• Staff can access any channel if needed"
            ),
            inline=False
        )

        help_embed.set_footer(
            text="Anti Stress Voice Channels • Type !helpvc for quick help or !commands for detailed list"
        )

        # Clear existing messages in help channel
        # async for message in help_channel.history(limit=100):
        #     await message.delete()

        # Send new help embed
        await help_channel.send(embed=help_embed)
        
        # Send confirmation to user
        confirm_embed = discord.Embed(
            title="✅ Help Updated",
            description=f"Command list has been posted in <#{help_channel_id}>",
            color=discord.Color.green()
        )
        await ctx.send(embed=confirm_embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to update help channel: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
