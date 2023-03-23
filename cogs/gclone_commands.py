"""Imports"""
import discord
from discord.ext import commands
import cogs._config
import cogs._helpers as hp
import subprocess
import time

# class CancelView(discord.ui.View):
#     def __init__(self,process:subprocess.Popen=None,author_id=None,logs=None,*args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.process= process
#         self.author_id = author_id
#         self.logs = logs

#     @discord.ui.button(label="Cancel",custom_id="button-1", style=discord.ButtonStyle.red, emoji="❌") 
#     async def button_callback1(self, button:discord.Button, interaction:discord.Interaction):
#         if not interaction.user.id == self.author_id:
#             return await interaction.response.send_message('you cannot do this',ephemeral=True)
#         self.process.terminate()
#         await interaction.response.send_message("Cancelled the task.")

#     @discord.ui.button(label="Logs Till Now",custom_id="button-2", style=discord.ButtonStyle.green) 
#     async def button_callback2(self, button:discord.Button, interaction:discord.Interaction):
#         if not interaction.user.id == self.author_id:
#             return await interaction.response.send_message('you cannot do this',ephemeral=True)
#         await interaction.response.send_message(f'```py\n{self.logs}\n```'[:1990],ephemeral=True)

class DoneView(discord.ui.View):
    def __init__(self,logs,author_id,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logs = logs
        self.author_id = author_id

    @discord.ui.button(label="Logs", style=discord.ButtonStyle.green) 
    async def button_callback(self, button:discord.Button, interaction:discord.Interaction):
        if not interaction.user.id == self.author_id:
            return await interaction.response.send_message('you cannot do this',ephemeral=True)
        i = len(self.logs) - 1980
        await interaction.response.send_message(f'```py\n{self.logs[i:]}\n```',ephemeral=True)

class Gclone(commands.Cog):
    """Gclone commands"""

    def __init__(self, bot):
        self.bot = bot
        self.clones = {}
    #     self.persistent_views_added = False

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     if not self.persistent_views_added:
    #         self.bot.add_view(CancelView(timeout=None))
    #         self.persistent_views_added = True


    async def cog_before_invoke(self, ctx):
        """
        Triggers typing indicator on Discord before every command.
        """
        await ctx.trigger_typing()    
        return

    @commands.command(aliases=['c'])
    async def clone(self,ctx:commands.Context,source=None,destination=None):
        if not source:
            return await ctx.send('Source url not provided.')
        # self.clones.update({ctx.message.id:source})
        util = hp.DriveUtil(ctx.author.id)
        try:
            s = util.getIdFromUrl(source)
        except IndexError:
            try:
                s = util.getIdFromUrl(util.make_url(source))
            except IndexError:
                s = source
        
        if not destination:d = cogs._config.default_destination_id
        else:
            try:
                d = util.getIdFromUrl(destination)
            except IndexError:
                try:
                    d = util.getIdFromUrl(util.make_url(destination))
                except IndexError:
                    d = destination

        name,size,mime = util.get_file_metadata(s)
        to_add= ''
        if mime == "application/vnd.google-apps.folder":
            to_add = f'/{name}' if name else ''

        cmd = [
            'gclone',
            'copy',
            'GC:{{{}}}'.format(s),
            'GC:{{{}}}'.format(d)+to_add,
            '--drive-server-side-across-configs',
            '--progress',
            '--stats',
            '1s',
            '--ignore-existing',
            '--transfers',
            '8',
            '--tpslimit',
            '6'
        ]

        msg = await ctx.send(embed=hp.embed('Cloning Started','You will get updates here....')[0])

        process = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
        
        # Poll the subprocess periodically for output
        logs = ''
        while True:
            # Wait for a short interval
            # Check if the subprocess has terminated
            last_updated = time.time()
            # Read any available output from the subprocess
            current_output = []
            while time.time()-last_updated < 7:
                output = process.stdout.readline()
                if not output and process.poll() is not None:
                    break
                if not output.decode().strip() == '':
                    data = output.decode().strip()
                    current_output.append(data)
                    logs+=f'{data}\n'
            if current_output == ['panic: runtime error: invalid memory address or nil pointer dereference']:
                return await ctx.send('Error, file\'s download quota has been exceeded. Can\'t clone sorry.')
                break
            # print((current_output))
            logs = logs.replace('-Transferred','-\nTransferred')
            strn = '\n'.join(current_output).replace('-Transferred','-\nTransferred')
            ls = strn.split('Transferred')
            x = 'Transferred'+'Transferred'.join(ls[-2:])
            i = len(x) - 4080
            if not x == '':
                await msg.edit(embed=hp.embed(title='Cloning in Progress...',description=f"```py\n{x[i:]}\n```")[0])
            else:
                break
            # print(f'##\n{x}\n##')
            if process.poll() is not None:
                await msg.edit(embed=hp.embed('Clone Complete',description=f"```py\n{x[i:]}\n```")[0],view=DoneView(logs,ctx.author.id))
                break

        process.communicate()
        return
    
    @commands.command(aliases=['s'])
    async def sync(self,ctx:commands.Context,source=None,destination=None):
        if not source:
            return await ctx.send('Source url not provided.')
        # self.clones.update({ctx.message.id:source})
        util = hp.DriveUtil(ctx.author.id)
        try:
            s = util.getIdFromUrl(source)
        except IndexError:
            try:
                s = util.getIdFromUrl(util.make_url(source))
            except IndexError:
                s = source
        
        if not destination:d = cogs._config.default_destination_id
        else:
            try:
                d = util.getIdFromUrl(destination)
            except IndexError:
                try:
                    d = util.getIdFromUrl(util.make_url(destination))
                except IndexError:
                    d = destination

        name,size,mime = util.get_file_metadata(s)
        to_add= ''
        if mime == "application/vnd.google-apps.folder":
            to_add = f'/{name}' if name else ''

        cmd = [
            'gclone',
            'sync',
            'GC:{{{}}}'.format(s),
            'GC:{{{}}}'.format(d)+to_add,
            '--drive-server-side-across-configs',
            '--progress',
            '--stats',
            '1s',
            '--transfers',
            '50',
            '--tpslimit',
            '50',
            '--checkers',
            '10',
            '-vP',
            '--drive-chunk-size',
            '128M',
            '--drive-acknowledge-abuse',
            '--drive-keep-revision-forever',
            '--fast-list'
        ]

        msg = await ctx.send(embed=hp.embed('Syncing Started','You will get updates here....')[0])

        process = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
        
        # Poll the subprocess periodically for output
        logs = ''
        while True:
            # Wait for a short interval
            # Check if the subprocess has terminated
            last_updated = time.time()
            # Read any available output from the subprocess
            current_output = []
            while time.time()-last_updated < 7:
                output = process.stdout.readline()
                if not output and process.poll() is not None:
                    break
                if not output.decode().strip() == '':
                    data = output.decode().strip()
                    current_output.append(data)
                    logs+=f'{data}\n'
            if current_output == ['panic: runtime error: invalid memory address or nil pointer dereference']:
                return await ctx.send('Error, file\'s download quota has been exceeded. Can\'t sync sorry.')
                break
            # print((current_output))
            logs = logs.replace('-Transferred','-\nTransferred')
            strn = '\n'.join(current_output).replace('-Transferred','-\nTransferred')
            ls = strn.split('Transferred')
            x = 'Transferred'+'Transferred'.join(ls[-2:])
            i = len(x) - 4080
            if not x == '':
                await msg.edit(embed=hp.embed(title='Syncing in Progress...',description=f"```py\n{x[i:]}\n```")[0])
            else:
                break
            # print(f'##\n{x}\n##')
            if process.poll() is not None:
                await msg.edit(embed=hp.embed('Sync Complete',description=f"```py\n{x[i:]}\n```")[0],view=DoneView(logs,ctx.author.id))
                break

        process.communicate()
        return

        


def setup(bot):
    bot.add_cog(Gclone(bot))
    print("Gclone cog is loaded")