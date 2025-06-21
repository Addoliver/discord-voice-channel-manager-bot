# Discord Voice Channel Manager Bot

A Discord bot for managing private voice channels with advanced features like whitelisting, blacklisting, and channel customization.

## Features

- Create custom voice channels
- Manage channel privacy (public/private)
- User management (whitelist/blacklist)
- Channel customization (name, size, bitrate)
- Voice controls (mute/unmute)
- User controls (ban/unban)
- Channel ownership management
- Help command system

## Setup

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Create a Discord Bot and Get Token:
   1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   2. Click "New Application" and give it a name
   3. Go to the "Bot" section and click "Add Bot"
   4. Click "Reset Token" and copy your bot token
   5. Enable necessary Privileged Gateway Intents (PRESENCE, SERVER MEMBERS, MESSAGE CONTENT)

3. Configure the `.env` file:

Create a file named `.env` in the root directory with the following content:
```env
# REQUIRED: Your Discord bot token (do not share this!)
DISCORD_TOKEN=your_bot_token_here

# Channel IDs for your server
# INFO_CHANNEL_ID is where the voice channel information will be posted
INFO_CHANNEL_ID=your_info_channel_id  # Required for auto-posting information
VOICE_CHANNEL_ID=your_voice_channel_id  # Optional
HELP_CHANNEL_ID=your_help_channel_id    # Optional
```

Important Notes:
1. Token Configuration:
   - DISCORD_TOKEN is required for the bot to function
   - Replace `your_bot_token_here` with your actual bot token
   - Never share your bot token with anyone
   - Do not commit the .env file to version control

2. Channel Configuration:
   - INFO_CHANNEL_ID is where voice channel information is posted
   - Information is automatically posted when the bot starts
   - Use `!vcinfo` to update the information
   - Old messages are automatically cleared before new posts
   - If INFO_CHANNEL_ID is not set, information posts in command channel
   - Other channel IDs are optional and can be added later

3. Invite Bot to Your Server:
   1. Go to OAuth2 > URL Generator in the Developer Portal
   2. Select "bot" and "applications.commands" scopes
   3. Select required permissions:
      - Manage Channels
      - Move Members
      - Mute Members
      - Deafen Members
      - View Channels
      - Send Messages
      - Manage Messages
   4. Copy and open the generated URL to invite the bot

4. Run the bot:
```bash
python bot.py
```

## How It Works

1. Information Display:
   - Use `!vcinfo` to see detailed information about voice channels
   - Shows available features, permissions, and size options
   - Displays public/private channel rules
   - Interactive buttons for quick channel creation

2. Voice Channel Creation:
   - Interactive buttons for quick channel creation
   - Choose from preset sizes (2-10 people) or unlimited
   - Custom size option available via command
   - Channels are created instantly upon button click
   - You're automatically moved to your new channel
   - Empty channels are automatically deleted

3. Channel Management:
   - Use commands to customize your channel
   - Only channel owners can modify settings
   - Channels are automatically cleaned up when empty

## Channel Size Options

Quick create buttons are available for:
- Duo (2 people) - Perfect for private conversations
- Trio (3 people) - Small group discussions
- Quad (4 people) - Standard team size
- Penta (5 people) - Medium group
- Hexa (6 people) - Larger discussions
- Septa (7 people) - Extended group
- Octa (8 people) - Large team size
- Deca (10 people) - Full team meetings
- Unlimited - Open channels
- Custom Size - Set your own limit

## Commands

### Channel Management
- `!create <name> [size]` - Create a new voice channel
- `!name <new_name>` - Change channel name
- `!size <limit>` - Set channel size limit
- `!info` - Display channel information

### Privacy Controls
- `!privacy` - Toggle channel privacy
- `!whitelist <user>` - Add user to whitelist
- `!blacklist <user>` - Add user to blacklist

### User Management
- `!mute <user>` - Mute a user
- `!unmute <user>` - Unmute a user
- `!ban <user>` - Ban user from channel
- `!unban <user>` - Unban user from channel
- `!guests add <user>` - Add user to guest list
- `!guests remove <user>` - Remove user from guest list
- `!guests list` - Show current guest list

### Channel Controls
- `!transfer <user>` - Transfer channel ownership
- `!reset` - Reset all channel settings
- `!host <user>` - Set a temporary host
- `!changehost <user>` - Change the channel host
- `!bitrate <value>` - Change channel bitrate

## Support

For a list of available commands, use `!commands` in Discord.
