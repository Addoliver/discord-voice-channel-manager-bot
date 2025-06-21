import discord
from discord.ext import commands

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

@commands.command(name='help')
async def help_command(ctx):
    """Show help information"""
    embed = discord.Embed(
        title="🎮 Voice Channel Help",
        description="Quick guide to voice channel commands and features",
        color=discord.Color.blue()
    )
    
    # Core Commands
    embed.add_field(
        name="📋 Basic Commands",
        value=(
            "`!create <name> [size]` Create a channel\n"
            "`!name <new_name>` Rename channel\n"
            "`!size <number>` Set member limit\n"
            "`!privacy` Toggle private mode"
        ),
        inline=False
    )
    
    # Management
    embed.add_field(
        name="⚙️ Management",
        value=(
            "`!whitelist <user>` Allow user\n"
            "`!blacklist <user>` Block user\n"
            "`!guests add/remove <user>` Manage guests\n"
            "`!host <user>` Set temporary host"
        ),
        inline=False
    )
    
    # Tips
    embed.add_field(
        name="💡 Tips",
        value=(
            "• Use buttons for quick channel creation\n"
            "• Set to private for invite-only access\n"
            "• Temporary hosts can manage users\n"
            "• Channels auto-delete when empty"
        ),
        inline=False
    )
    
    embed.set_footer(text="Type !commands for full command list")
    await ctx.send(embed=embed)
