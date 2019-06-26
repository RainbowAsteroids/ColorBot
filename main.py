#https://discordapp.com/api/oauth2/authorize?client_id=592772548949835807&permissions=268503072&scope=bot
import discord, asyncio, json, random, os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

client = discord.Client()
token = ""
ready = False #When the bot isn't ready, it should be False.
guilds = None

invite_url = "https://discordapp.com/api/oauth2/authorize?client_id=592772548949835807&permissions=268503072&scope=bot"
helptext = """```
!color is the prefix used
help - this text
leave - leaves this guild and cleans up
invite - bot invite url
```"""

async def permission(message, permission='manage_messages'):
    if eval(f"message.channel.permissions_for(message.author).{permission}"):
        return True
    else:
        await message.channel.send(f'<@{message.author.id}> Hmm... seems like you don\'t have the "{permission}" permission, so I can\'t let you do that.')
        return False

async def leave(guild):
    await guild.get_role(guilds[guild.id]["service_role"]).delete()
    await guild.leave()

async def get_guilds():
    #Grab the current guilds from the API and the saved guilds
    #Get rid of guilds the bot isn't in and leave the guilds we are in
    current_guilds = client.guilds
    current_guild_ids = [guild.id for guild in current_guilds]

    unmapped_saved_guilds = json.loads(open('guilds.json').read())
    saved_guilds = {}
    for id in unmapped_saved_guilds: #Make the ids ints
        saved_guilds[int(id)] = unmapped_saved_guilds[id]
    saved_guilds_immutable = dict(saved_guilds) #To avoid runtime error, reference this dict only
    new_guilds = []
    for guild in current_guilds:
        if not guild.id in saved_guilds.keys():
            new_guilds.append(guild)
    
    for id in saved_guilds_immutable.keys():
        if not id in current_guild_ids:
            del saved_guilds[id]
    
    for guild in new_guilds:
        await guild.owner.send("In order to make sure the bot inviting process goes smoothly, it's important to re-invite me.\nhttps://discordapp.com/api/oauth2/authorize?client_id=592772548949835807&permissions=268503072&scope=bot")
        await guild.leave()
        
    return saved_guilds
        

async def update():
    #Update the JSON file
    open('guilds.json','w').write(json.dumps(guilds))

def random_color():
    return discord.Color.from_rgb(
        random.randrange(256),
        random.randrange(256),
        random.randrange(256))


@client.event
async def on_ready():
    global ready
    global guilds
    ready = True
    print(f"Logged in as {client.user.name}")
    guilds = await get_guilds()
    await update()
    await client.change_presence(activity=discord.Game(name="!color help"))
    while True:
        if guilds == None: continue #Skip while that async function is running
        await asyncio.sleep(5)
        if ready:
            for id in guilds:
                guild = client.get_guild(id) # Grab the real guild
                await guild.get_role(guilds[id]["service_role"]).edit(color=random_color()) #Set random color

@client.event
async def on_disconnect():
    global ready
    ready = False

@client.event
async def on_message(message):
    #Implement some command stuff here
    if message.content.lower().startswith('!color'):
        command = message.content.lower().split(' ')[1:]
        if len(command) == 0 or command[0] == 'help':
            await message.channel.send(helptext)
        elif command[0] == 'leave':
            if await permission(message, 'manage_guild'):
                await message.channel.send("Goodbye!")
                await leave(message.guild)
        elif command[0] == 'close':
            if message.author.id == 250376950147842048:
                await client.close()
        elif command[0] == 'invite':
            await message.channel.send(f"<@{message.author.id}> {invite_url}")
        else:
            await message.channel.send(helptext)

@client.event
async def on_guild_join(guild):
    #Tell the owner how to setup bot
    #Log the important roles to not_set_up
    await asyncio.sleep(1)
    info = '''Hello there <@{}>! {} is a bot that changes the user color of certain users after 5 seconds. It does this by editing the color of a service role to a random color. If you're wondering how roles work, read Discord's Role Management 101 (https://support.discordapp.com/hc/en-us/articles/214836687-Role-Management-101). I've made a role by the name of "Color Changing Role". Feel free to change the name of the role and/or any other properties. Just make sure to keep my highest role above the service role.'''
    main_role = guild.me.top_role
    service_role = await guild.create_role(
        reason=f"{client.user.name}'s service role", 
        name="Color Changing Role")
    guilds[guild.id] = {
        "main_role":main_role.id,
        "service_role":service_role.id,
    }
    
    for member in guild.members:
        if member.guild_permissions.manage_roles:
            await member.send(info.format(member.id, client.user.name))


    await update()

@client.event
async def on_guild_remove(guild):
    try:
        del guilds[guild.id]
    except TypeError:
        pass
    
    await update()

"""
@client.event
async def on_guild_role_update(_, __):
    #Make sure the guild is in not_set_up
    #Check if guild is set up
    #If set up, remove from not_set_up
    #If went from set up to not set up, then alert the owner
    await asyncio.sleep(1)
    guild = _.guild
    if guilds[guild.id]["setup"]: return
    main_role = (guilds[guild.id]["main_role"])
    service_role = (guilds[guild.id]["service_role"])
    if main_role == guild.roles[-1].id and service_role == guild.roles[-2].id:
        guilds[guild.id]["setup"] = True
        await guild.owner.send("Setup Complete! You can now move the roles as you wish. Just make sure my highest role is above the service role.")

    await update()
"""

client.run(token)