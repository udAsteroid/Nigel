import nextcord, os, asyncio, datetime, pytz, random, json, ephem
from nextcord.ext import commands, tasks, application_checks
import numpy as np
from dotenv import load_dotenv

def moonemoji():
    # Create a Moon object
    moon = ephem.Moon()
    moon.compute()

    # Get the moon phase (0 to 1, where 0=new, 0.5=full, 1=new)
    phase = moon.moon_phase

    # Determine the corresponding emoji based on the phase
    if 0 <= phase < 0.125:
        return "🌑"
    elif 0.125 <= phase < 0.25:
        return "🌒"
    elif 0.25 <= phase < 0.375:
        return "🌓"
    elif 0.375 <= phase < 0.5:
        return "🌔"
    elif 0.5 <= phase < 0.625:
        return "🌕"
    elif 0.625 <= phase < 0.75:
        return "🌖"
    elif 0.75 <= phase < 0.875:
        return "🌗"
    else:
        return "🌘"

#descs = ["Do you remember..."]
moondescs = ["Come for the insomnia, stay for the sleep deprivation.", "Why are you still awake?", "Sleep isn't too important... right?", "What even is the name for this place?", "Turn your brightness down...", "Well, at least until 6am...", "How many hours of sleep are you getting?", "This took too long to make...", "Welcome to the Jungle!", "According to all known laws of aviation...", "Literally 1984", "And soon it'll be one", "Return tomorrow for more", "NIGEL JUMPSCARE!", "why do we bake cookies and cook bacon?", "go to bed", "time to start a cult!!", "first person to use the 🌙 emoji gets free macaroni (please share some with me)", "1+1= what?", "goose go HJÖNK"]
stardescs = ["You shouldn't be here...", "Go to sleep. Go straight to sleep. Do not check discord, do not collect phone", "So many stars in the night sky...", "Maddie better not be here...", "3am challenge :o"]

TESTING_GUILD_ID = 1005796350396469268  # Replace with your guild ID

intents = nextcord.Intents.default()
intents.members = True

queues = {}

bot = commands.Bot(intents=intents)
client = nextcord.Client(activity=nextcord.Game(name='At your service.'))

load_dotenv()

@bot.event
async def on_ready():
    print(f'We have logged in on docker with persistent data as {bot.user}! Current time is {datetime.datetime.now(pytz.timezone("Australia/Melbourne")).hour}!')

@bot.event
async def on_message(message):
    if not os.path.isfile('data/users.json'):
        with open('data/users.json', 'w') as f:
            json.dump({}, f)

    with open('data/users.json', 'r') as f:
        users = json.load(f)

    if message.author.bot:
        return

    if str(message.author.id) not in users:
        users[str(message.author.id)] = {}
        users[str(message.author.id)]['messages'] = 1
        users[str(message.author.id)]['username'] = message.author.name

    users[str(message.author.id)]['messages'] += 1

    with open('data/users.json', 'w') as f:
        json.dump(users, f, indent=4)

    await bot.process_commands(message)

@tasks.loop(seconds=10.0)
async def looptask():
    await bot.wait_until_ready()
    moonchannel = bot.get_channel(1108002952158904401)
    starchannel = bot.get_channel(1191342973447847956)
    role = moonchannel.guild.get_role(1006024662351876136)
    moonperms = moonchannel.overwrites_for(role)
    starperms = starchannel.overwrites_for(role)
    
    # MOON
    if datetime.datetime.now(pytz.timezone("Australia/Melbourne")).hour >= 6:
        if moonperms.read_messages == True:
            await moonchannel.set_permissions(role, read_messages=False)
    else:
        if not moonperms.read_messages:
            await moonchannel.set_permissions(role, read_messages=True)
            embed=nextcord.Embed(title="As the clock strikes twelve, it opens...", description=random.choice(moondescs), color=0x610085)
            await moonchannel.send(embed=embed, files=[nextcord.File('gotosleepcompressed.mp4')])
            await moonchannel.edit(name=moonemoji())
    
    # STAR
    if datetime.datetime.now(pytz.timezone("Australia/Melbourne")).hour != 3:
        if starperms.read_messages == True:
            await starchannel.set_permissions(role, read_messages=False)
    else:
        if not starperms.read_messages:
            await starchannel.set_permissions(role, read_messages=True)
            embed=nextcord.Embed(title="At the darkest part of night...", description=random.choice(stardescs), color=0x202763)
            await starchannel.send(embed=embed)

@bot.slash_command(description="Add all users to JSON data file.", guild_ids=[TESTING_GUILD_ID])
async def add_all_users(interaction: nextcord.Interaction):
    await interaction.response.defer()
    if not os.path.isfile('data/users.json'):
        with open('data/users.json', 'w') as f:
            json.dump({}, f)

    with open('data/users.json', 'r') as f:
        users = json.load(f)
        print("Loaded JSON!")
        print(interaction.guild.fetch_members())
        for member in interaction.guild.members:
            if member.bot:
                continue
            if str(member.id) not in users:
                users[str(member.id)] = {}
                users[str(member.id)]['messages'] = 0
                users[str(member.id)]['username'] = member.name
                print(f"Added data for {member.id} ({member.name})!")

    with open('data/users.json', 'w') as f:
        json.dump(users, f, indent=4)
    await interaction.followup.send("All users have been added to the JSON data file.")

@bot.slash_command(description="Set user JSON variable content", guild_ids=[TESTING_GUILD_ID])
async def set_user_json(interaction: nextcord.Interaction, user: nextcord.Member, var: str, val: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You are not authorized to run this command.", ephemeral=True)
    else:
        if not os.path.isfile('data/users.json'):
            await interaction.response.send_message("There is no user JSON file! Run `/add_all_users`.")
        else:
            with open('data/users.json', 'r') as f:
                users = json.load(f)
                if str(user.id) in users:
                    users[str(user.id)][var] = val
                    users[str(user.id)]["messages"] = int(users[str(user.id)]["messages"])
                    with open('data/users.json', 'w') as f:
                        json.dump(users, f, indent=4)
                    msg = "Successfully set %s to %s for %s!" % (var, val, user.name)
                    await interaction.response.send_message(msg)
                else:
                    await interaction.response.send_message("Member not initiated! They must send a message, or you can run `/add_all_users`.", ephemeral=True)

@bot.slash_command(description="Ping!", guild_ids=[TESTING_GUILD_ID])
async def ping(interaction: nextcord.Interaction):
    await interaction.response.defer()
    await interaction.send("Pong!")

@bot.slash_command(description="Sends the gotosleep video!", guild_ids=[TESTING_GUILD_ID])
async def gotosleep(interaction: nextcord.Interaction):
    await interaction.response.defer()
    await interaction.send(files=[nextcord.File('gotosleepcompressed.mp4')])

@bot.slash_command(description="At your service.", guild_ids=[TESTING_GUILD_ID])
async def nigelbillingsley(interaction: nextcord.Interaction):
    await interaction.send("Welcome to Jumanji. I've been so anxious for your arrival. As you know, Jumanji is in grave danger. We're counting on the four of you to lift the curse. The fate of Jumanji is in your hands. The goal for you. I'll recite in verse. Return the jewel and lift the curse. If you wish to leave the game, you must save Jumanji and call out its name.")
    
@bot.slash_command(description="Gain Nigel's dominion.", guild_ids=[TESTING_GUILD_ID])
async def blessing(interaction: nextcord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You are not worthy of my blessing.")
    else:
        knownrole = nextcord.utils.get(interaction.guild.roles, name="Nigel's Blessing")
        await interaction.user.add_roles(knownrole)
        await interaction.send("You have gained my blessing.")
        await asyncio.sleep(60*5)
        await interaction.user.remove_roles(knownrole)

@bot.slash_command(description="Rank members based on their messages", guild_ids=[TESTING_GUILD_ID])
async def rank_members(interaction: nextcord.Interaction):
    if not os.path.isfile('data/users.json'):
        await interaction.response.send_message("There is no user JSON file! Run `/add_all_users`.")
    else:
        with open('data/users.json', 'r') as f:
            users = json.load(f)
            sorted_users = sorted(users.items(), key=lambda x: x[1]['messages'], reverse=True)
            rank = 1
            embed = nextcord.Embed(title="Ranking of TOP 25 members based on their messages", color=0x610085)
            for user in sorted_users:
                if rank <= 25:
                    embed.add_field(name=f"{rank}. {user[1]['username']}", value=f"{user[1]['messages']} messages", inline=False)
                    rank += 1
            embed.set_footer(text="Note that this does not account for deleted messages!")
            await interaction.response.send_message(embed=embed)

looptask.start()
bot.run(os.getenv("TOKEN"))