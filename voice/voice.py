import discord
from discord.ext import commands
from cogs.db import Connect
import datetime
import configparser

class Voice(commands.Cog):
	def __init__(self, bot):
		cfg = configparser.ConfigParser()
		cfg.read("cogs/roles.ini")
		self.bot = bot
		self.users = {}
		self.color = 0xff7733
		
		if len(cfg['ROLES']) != len(cfg['PRISE']):
			raise Exception("Config is wrong!")
		else:
			self.roles = {}
			for i in range(1, len(cfg['ROLES'])+1):
				self.roleCount = len(cfg['ROLES'])
				id = int(cfg['ROLES'][f'role{i}'])
				prise = int(cfg['PRISE'][f'role{i}'])
				self.roles[f'role{i}'] = {'id': f'{id}', 'prise': prise}
				
	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		if member.bot:
			return
		if member == self.bot.user:
			return
		
		if after.channel and before.channel:
			pass
		elif before.channel:
			db = Connect.conn()
			cur = db.cursor()

			cur.execute(f"SELECT startTime FROM users WHERE id = {member.id}")
			dbExecution = cur.fetchall()
			print(dbExecution)
			if not dbExecution:
				return

			time = datetime.datetime.now()
			time_old = dbExecution[0][0]

			print(time)
			print(time_old)
			
			timedelta = time - time_old

			print(timedelta)
			
			cur.execute(f'SELECT voiceTime FROM users WHERE id = {member.id}')
			timeOld_r = cur.fetchall()
			print(timeOld_r)
			if not timeOld_r:
				maxRole = None
				for i in range(1, self.roleCount+1):
					if self.roles[f'role{i}']['prise'] <= timedelta.total_seconds():
						maxRole = f"role{i}"

				if maxRole:
					role = discord.utils.get(member.guild.roles, id=int(self.roles[maxRole]['id']))
					await member.add_roles(role)

					await member.send(f"{member.mention} поздравляю! Ты достиг роли `{role.name}`!")
				cur.execute(f"INSERT INTO users(id, voiceTime) VALUES ({member.id}, {timedelta.total_seconds()})")
				db.commit()
			else:
				
				maxRole = None
				timeOld = datetime.timedelta(seconds=timeOld_r[0][0])
				print(timeOld)
				timeNew = timeOld + timedelta
				print(timeNew)
				for i in range(1, self.roleCount+1):
					if self.roles[f'role{i}']['prise'] <= timeNew.total_seconds():
						maxRoleN = i-1
						maxRole = f"role{i}"

				if maxRole:
					role = discord.utils.get(member.guild.roles, id=int(self.roles[maxRole]['id']))
					if maxRoleN != 0:
						roleOld = discord.utils.get(member.guild.roles, id=int(self.roles[f"role{maxRoleN}"]['id']))
				
						await member.remove_roles(roleOld)
	
					await member.add_roles(role)
					await member.send(f"{member.mention} поздравляю! Ты достиг роли `{role.name}`!")


				cur.execute(f"UPDATE users SET voiceTime = {timeNew.total_seconds()} WHERE id = {member.id}")
				db.commit()
			
			db.close()

		elif after.channel:
			time = datetime.datetime.now()
			db = Connect.conn()
			cur = db.cursor()
			time = f"{time.year}-{time.month}-{time.day} {time.hour}:{time.minute}:{time.second}"
			cur.execute(f"SELECT * FROM users WHERE id = {member.id}")
			if not cur.fetchall():
				cur.execute(f"INSERT INTO users(id, voiceTime, startTime) VALUES ({member.id}, 0, '{time}')")
				db.commit()
				db.close()
			else:
				cur.execute(f"UPDATE users SET startTime = '{time}' WHERE id = {member.id}")
				db.commit()
				db.close()

	@commands.command(aliases=["время", "time", "dhtvz", "ешьу"])
	async def _time(self, ctx):
		await ctx.message.delete()
		emb = discord.Embed(title="voice time", colour= self.color)
		emb.set_author(name= self.bot.user.name, icon_url=self.bot.user.avatar_url)
		emb.set_footer(text= "Запросил " + ctx.message.author.display_name, icon_url= ctx.message.author.avatar_url)

		db = Connect.conn()
		cur = db.cursor()
		cur.execute(f"SELECT voiceTime FROM users WHERE id = {ctx.author.id}")
		f = cur.fetchall()
		if not f:
			res = "Вы еще не заходили в голосовой канал!"
		else:
			time = datetime.timedelta(seconds=f[0][0])
			res = f"{time}"

		emb.add_field(name="Голосовой онлайн", value= res)
		await ctx.send(embed=emb)
		db.close()
		

	@commands.command(aliases=['top', 'топ', 'еоз', 'njg'])
	async def _top(self, ctx):
		await ctx.message.delete()
		emb = discord.Embed(title= "top", colour=self.color)
		emb.set_author(name= self.bot.user.name, icon_url=self.bot.user.avatar_url)
		emb.set_footer(text= "Запросил " + ctx.message.author.display_name, icon_url= ctx.message.author.avatar_url)

		db = Connect.conn()
		cur = db.cursor()
		cur.execute(f'SELECT * FROM users ORDER BY voiceTime DESC LIMIT 0, 10')
		res = cur.fetchall()
		num = 0
		for i in res:
			num += 1
			try:
				usr = self.bot.get_user(i[0])
				time = datetime.timedelta(seconds=int(i[1]))
				emb.add_field(name=f"{num}.{usr.name}", value=f"{time}", inline=True)
			except Exception:
				pass
		
		await ctx.send(embed= emb)

def setup(bot):
	bot.add_cog(Voice(bot))
	print("[INFO] Voice loaded")
