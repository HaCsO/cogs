import discord
import asyncio
import configparser
from discord.ext import commands
from discord.ext.commands import Bot

class GamesCog(commands.Cog, name='Games'):
	def __init__(self, Bot):
		cfg = configparser.ConfigParser()
		cfg.read("cogs/roles.ini") # Конфиг
		self.bot = Bot
		self.rrg = {}
		self.count = 0
		self.selectedPage = 0
		for i in cfg['GAMES']:
			self.count += 1
			self.rrg[f'game{self.count}'] = {'role': int(cfg['ROLES'][f'role{self.count}']), 'react': int(cfg['REACTS'][f'react{self.count}']), 'name': cfg['GAMES'][f'game{self.count}']}
		
		self.pages = []
		pageNum = 0
		page = []
		for i in range(len(self.rrg)):
			
			i += 1
			if i > 10:
				pageNum += 1
				self.pages.append(page)
				page = []

			page.append(self.rrg[f'game{i}'])

			if i == len(self.rrg):
  				self.pages.append(page)
				
	async def sysR(self, msg):
		r1 = self.bot.get_emoji(667105734114148353)
		r2 = self.bot.get_emoji(667105735515045898)
		r3 = self.bot.get_emoji(666299737418498050)
		await msg.add_reaction(r1)
		await msg.add_reaction(r2)
		await msg.add_reaction(r3)

	async def fetchPage(self, selectedPage):
		emb = discord.Embed(title="Параметры комманды `!games`", description="Для получения роли выберите соответствующюю реакцию из списка ниже:", colour=0xff0077)
		
		
		for j in self.pages[selectedPage]:

			emb.add_field(name=f"{j['name']}", value=f"{self.bot.get_emoji(j['react'])}")

		return emb

	async def fetchReacts(self, msg, selectedPage):
		for i in self.pages[selectedPage]:
			await msg.add_reaction(self.bot.get_emoji(i['react']))
			
	@commands.command()
	async def games(self, ctx):
		await ctx.message.delete()
		

		emb = await self.fetchPage(self.selectedPage)

		rightBlock = False
		leftBlock = True

		msg = await ctx.send(embed= emb)
		await self.sysR(msg)
		await self.fetchReacts(msg, self.selectedPage)

		def check(r, u):
			return u.id == ctx.author.id

		while 1:

			try:
				react, user= await self.bot.wait_for('reaction_add', check=check, timeout = 120)
			except asyncio.TimeoutError:
                            await msg.delete()
                            break
			await react.remove(ctx.author)
			for i in self.pages[self.selectedPage]:
				if react.emoji.id == i['react']:
					
					role = discord.utils.get(ctx.message.guild.roles, id= i['role'])
					if role in ctx.author.roles:
						await ctx.author.remove_roles(role)
					else:
						await ctx.author.add_roles(role)
	
			if react.emoji.id == 667105735515045898:
				
				leftBlock = False
				if rightBlock:
					
					continue
				self.selectedPage += 1
				

				emb = await self.fetchPage(self.selectedPage)
				await msg.edit(embed= emb)
				await msg.clear_reactions()

				await self.sysR(msg)
				await self.fetchReacts(msg, self.selectedPage)

				if self.selectedPage+1 == len(self.pages):
					rightBlock = True
					
					continue

			elif react.emoji.id == 667105734114148353:
				rightBlock = False
				if leftBlock:
					
					continue 
				leftBlock = False
				self.selectedPage -= 1

				emb = await self.fetchPage(self.selectedPage)
				await msg.edit(embed= emb)
				await msg.clear_reactions()

				await self.sysR(msg)
				await self.fetchReacts(msg, self.selectedPage)

				if self.selectedPage == 0:
					leftBlock = True
					continue

			elif react.emoji.id == 666299737418498050:
				await msg.delete()
				break





def setup(Bot):
	Bot.add_cog(GamesCog(Bot))
	print('[INFO] Games успешно загружен')
