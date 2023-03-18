import logging
from discord.ext import commands
import discord
import os
import cogs._config
import os
import traceback
from datetime import datetime

def embed(title,description,url=None):
    em = discord.Embed(title=title,description=description,color=discord.Color.green(),url="https://github.com/jsmsj/gdriveclonebot",timestamp=datetime.now())
    em.set_footer(text="Made with 💖 by jsmsj.")
    if url:
        btn = discord.ui.Button(label="Link",url=url)
        view = discord.ui.View()
        view.add_item(btn)
        return [em,view]
    return [em,None]

if os.path.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)

logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    handlers=[logging.FileHandler('log.txt'), logging.StreamHandler()],
                    level=logging.INFO)

logger = logging.getLogger(__name__)

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=cogs._config.prefix, intents=intents, case_insensitive=True) 

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Gclone x Discord"))
    print("Bot is ready!")

@bot.event
async def on_command_error(ctx:commands.Context,error):
    if hasattr(ctx.command, 'on_error'):
        return
    if isinstance(error,commands.CommandNotFound):
        return
    if isinstance(error,commands.CheckFailure):
        return
    else:
        logger.warning(error,exc_info=True)
        logger.warning(traceback.format_exc())
        _file=None
        if os.path.exists('log.txt'):
            _file = discord.File('log.txt')
        await ctx.send(embed=embed(f'Error | {ctx.command.name}',f'An error occured, kindly report it to jsmsj#5252.\n```py\n{error}\n```\nHere is the attached logfile.')[0],file=_file)

@bot.command(description="Shows the bot's latency")
async def ping(ctx):
    await ctx.send(f"🏓 {round(bot.latency*1000)}ms")


@commands.is_owner()
@bot.command(description='logfile')
async def log(ctx):
    if os.path.exists('log.txt'):
        await ctx.send(embed=embed('📃 Log File','Here is the log file')[0],file=discord.File('log.txt'))
    else:
        await ctx.send(embed=embed('📃 Log File','No logfile found :(')[0])


        
if __name__ == '__main__':
    # When running this file, if it is the 'main' file
    # i.e. its not being imported from another python file run this
    for file in os.listdir("cogs/"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")
    
    bot.load_extension('jishaku')

    logger.info("Bot has started, all cogs are loaded.")

    #  CHECKS

    if not cogs._config.default_destination_id :
        raise NameError('There is no default_destination_id in .env')
    
    try:
        x = os.listdir('accounts')
        if len(x) == 0:
            raise IndexError('There are no service account files in accounts folder')
    except FileNotFoundError:
        raise ValueError('There is no folder named accounts')
        
    bot.run(cogs._config.bot_token)

