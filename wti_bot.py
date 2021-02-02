import requests
import discord

from discord.ext import commands

URL_LINK = 'https://rest.wti.com'
pathway_extras = '/api/v2/status/'

USERNAME = 'restpowerpublic'
PASSWORD = 'restfulpassword'

API_KEY = 'key'

client = commands.Bot(command_prefix='-', help_command=None)


def get_json(suffix_word=''):
    """Gets a json from the webserver and returns it"""
    try:
        r = requests.get(
            URL_LINK + pathway_extras + suffix_word,
            auth=(USERNAME, PASSWORD),
            verify=True,
        )

    except requests.exceptions.RequestException:
        print('Something went wrong when trying to fetch the json file')
    else:
        return r.json()


@client.event
async def on_ready():
    print(f'We are logged in as {client.user}')


@client.command(
    aliases=['?', 'commands'],
    help='Displays all avaliable commands',
    )
@commands.has_role('@everyone')
async def help(ctx, args=None):
    embed = discord.Embed(
        title='Help',
        color=discord.Color.blue()
    )

    embed.set_footer(text='WTI Bot v1.1')
    command_names_list = [x.name for x in client.commands]

    if not args:
        embed.add_field(
            name='List of avaliable commands:',
            value='\n'.join([str(i+1) + '. '+x.name for i, x in (enumerate(client.commands))]),
            inline=False,
        )
    elif args in command_names_list:
        embed.add_field(
            name=args,
            value=client.get_command(args).help
        )
    else:
        embed.add_field(
            name='Nuh uh',
            value='No command for that!'
        )
    await ctx.send(embed=embed)


@help.error
async def help_error(ctx, error):
    await ctx.channel.send(f'{error}')


@client.command(help='Change the host url to another box\nMust have admin role\nParams: ip apikey')
@commands.has_role('Admin')
async def host(ctx, ip, apikey):
    global URL_LINK
    old_pathway = URL_LINK
    if (apikey == API_KEY):
        URL_LINK = ip
        await ctx.channel.send(f'[✔️] API key accepted!\nYou entered the new URL: {ip}\n\tOld URL is {old_pathway}')
    else:
        await ctx.channel.send('[❌] Invalid Command')


@host.error
async def host_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.channel.send('You do not have permission to run this command')
    else:
        await ctx.channel.send('An unexpected error occured, please try again')


@client.command(aliases=['change_data', 'change_password', 'change_username', 'password'], help='Change the username and password to the box\nParams: username password apikey')
@commands.has_role('Admin')
async def creds_change(ctx, username, password, apikey):
    global USERNAME, PASSWORD
    old_username, old_password = USERNAME, PASSWORD
    if(apikey == API_KEY):
        USERNAME = username
        PASSWORD = password
        await ctx.channel.send(f'[✔️] API key accepted!\nYou entered new credentials:\nNew Username: {USERNAME}\tOld Username: {old_username}\nNew Password: {PASSWORD}\tOld Password: {old_password}')
    else:
        await ctx.channel.send('[❌] Invalid Command')


# @client.command(aliases=['get_username', 'get_password', 'username'])
# async def get_creds(ctx):
#     await ctx.channel.send(f'Current Username: {USERNAME}\nCurrent Password: {PASSWORD}')


@client.command(aliases=['url', 'link', ], help='Returns the current url')
async def geturl(ctx):
    await ctx.channel.send(f'Current URL: {URL_LINK}')


@client.command(aliases=['temperature', ], help='Returns the temperature of the current box')
async def temp(ctx):
    response = get_json('temperature')
    box_temp = response['temperature']
    box_unit = response['format']
    await ctx.channel.send(f'The temperature of {URL_LINK} is: {box_temp}{box_unit}')


@client.command(help='Returns of the power of the current box')
async def power(ctx):
    response = get_json('power')
    branchcount = response['branchcount']
    plugsper_branch = int(response['plugcount']) / int(branchcount)
    embed = discord.Embed(
        title='Power Branches',
        description='This is the power statistics of the box',
        color=discord.Color.blurple(),
    )
    embed.set_footer(text=f'Power of {URL_LINK}')

    for branch in range(1, int(branchcount) + 1):
        embed.add_field(
            name=f'Branch{branch}',
            value=f"{response['powerdata'][0][f'branch{branch}'][0]['voltage1']}V",
            inline=True,
        )

    # Send the branches out
    await ctx.channel.send(embed=embed)

    embed = discord.Embed(
        title='',
        description='This is the plug statistics of the box',
        color=discord.Color.blurple(),
    )
    embed.set_footer(text=f'Plugs of {URL_LINK}')

    for branch in range(1, int(branchcount) + 1):
        embed = discord.Embed(
            title=f'Plugs for Branch{branch}',
            description='This is the plug statistics of the box',
            color=discord.Color.blurple(),
        )
        embed.set_footer(text=f'Plugs of {URL_LINK}')

        for plug in range(1, int(plugsper_branch) + 1):
            embed.add_field(
                name=f'Plug{plug}',
                value=f"{response['powerdata'][0][f'branch{branch}'][0][f'current{plug}']}V",
                inline=True,
            )
        await ctx.channel.send(embed=embed)


@client.command(help='Returns the current of the box')
async def current(ctx):
    response = get_json('current')
    branchcount = response['branchcount']
    embed = discord.Embed(
        title='Current',
        description='This the current of the box',
        color=discord.Color.blurple(),
    )
    embed.set_footer(text=f'Current of {URL_LINK}')

    for branch in range(1, int(branchcount) + 1):
        embed.add_field(
            name=f'Branch{branch}',
            value=f"{response['powerdata'][0][f'branch{branch}'][0]['current1']}A",
            inline=True,
        )

    await ctx.channel.send(embed=embed)


@client.command(help='Returns of the alarms of the box')
async def alarms(ctx):
    response = get_json('alarms')
    alarms_list = []
    for alarm in response['alarms']:
        alarms_list.append(alarm['status'])

    embed = discord.Embed(
        title='Alarms',
        description='These are the alarms for the current box',
        color=discord.Color.red() if '1' in alarms_list else discord.Color.green(),
    )

    embed.set_footer(text=f'Alarms of {URL_LINK}')

    for alarm in response['alarms']:
        embed.add_field(
            name=alarm['name'],
            value='ok' if '0' in alarm['status'] else '!! ALERT !!',
            inline=False,
        )

    await ctx.channel.send(embed=embed)


@client.command(help='Returns of the firmware of the box')
async def firmware(ctx):
    response = get_json('firmware')
    box_firmware = response['config']['firmware']
    box_family = response['config']['family']
    if box_family == '0':
        box_family = 'VMR'
    elif box_family == '1':
        box_family = "DSM/CPM"
    else:
        box_family = "UNKNOWN"
    await ctx.channel.send(f'The firmware of {URL_LINK} is:\nFirmware: {box_firmware}\nProduct Family: {box_family}')


@client.command(help='Returns of the status of the box')
async def status(ctx):
    response = get_json()

    embed = discord.Embed(
        title='Status',
        description='This is the status of the box',
        color=discord.Color.blurple(),
    )

    embed.set_footer(text=f'Status of {URL_LINK}')

    embed.add_field(
        name='Vendor',
        value=response['vendor'].upper(),
        inline=False,
    )
    embed.add_field(
        name='Site ID',
        value=response['siteid'],
        inline=False,
    )
    embed.add_field(
        name='Product',
        value=response['product'],
        inline=False,
    )
    embed.add_field(
        name='Software Version',
        value=response['softwareversion'],
        inline=False,
    )
    embed.add_field(
        name='Serial Number',
        value=response['serialnumber'],
        inline=False,
    )
    embed.add_field(
        name='CPU Make',
        value=response['cpu_boardprogramdate'],
        inline=False,
    )
    embed.add_field(
        name='API Release',
        value=response['apirelease'],
        inline=False,
    )
    embed.add_field(
        name='Restful API',
        value=response['restful'],
        inline=False,
    )

    await ctx.channel.send(embed=embed)


@client.command(help='Says hello back to you')
async def hello(ctx):
    await ctx.channel.send('Hi!')

client.run('token')
