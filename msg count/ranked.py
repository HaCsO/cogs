import discord
from discord.ext import commands
from cogs.dbconnect import *

#Канал в который будут присылаться сообщения о новом уровне, если у пользователя отключенны личные сообщения
channel = 3472435432785

class Rank(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.users = {}
	
	# Команда для того что бы посчитать все сообщения на сервере за время его существования
	@commands.command()
	@commands.is_owner()
	async def parse(self, ctx):
		await ctx.send("Парсинг даты начался!")
		for i in ctx.message.guild.text_channels:
			async for msg in i.history(limit=None):
				try:
					self.users[f'{msg.author.id}'] += 1
				except KeyError:
					self.users[f'{msg.author.id}'] = 1

		for i in self.users:
			msgs = self.users[i]
			xp = msgs * 25
			lvl = 1
			while xp:
				if xp >= 1000+100*lvl:
					xp -= 1000+100*lvl
					lvl += 1
				else:
					break
			
			db = Connect.conn()
			cur = db.cursor()
			cur.execute(f"UPDATE users SET lvl={lvl}, xp={xp}, msg={msgs} WHERE id = {i}")
			db.commit()
			db.close()
		await ctx.send("Парсинг окончился!")

	

		
	@commands.Cog.listener()
	async def on_message(self, msg):
		if msg.author == self.bot.user:
			pass
		elif discord.ChannelType.private in msg.type:
			pass
		else:
			db = Connect.conn()
			curs = db.cursor()
			curs.execute(f"SELECT * FROM users WHERE id={msg.author.id}")
			res = curs.fetchall()
			if not res:
				curs.execute(f"INSERT INTO users (id, xp, lvl, msg) VALUES ({msg.author.id}, 50, 1, 1)")
				db.commit()
				db.close()
			else:
				res = res[0]
				lvl = res[2]
				xp = res[1]
				msgR = res[3]
				msgR += 1
				c = self.bot.get_channel(channel)
				xp += 25

				if xp == 1000 + 100 * lvl:
					xp = 0
					lvl += 1
					try:
						await msg.author.send(f"Поздравляю! Вы получили levelup! Теперь ваш уровень **{lvl}**")
					except Exception:
						await c.send(f"{msg.author.mention} Так как у тебя выключен лс, напишу тут, поздравляю! Ты достиг **{lvl}** уровня!", delete_after=15)
				else:
					pass

				curs.execute(f"UPDATE users SET lvl={lvl}, xp={xp}, msg={msgR} WHERE id={msg.author.id}")
				db.commit()
				db.close()
		


	@commands.command()
	async def top(self, ctx, arg = None):
		"""Выводит топ 10 активистов по 2 критериям, **msg** и **lvl**"""
		await ctx.message.delete()
		if arg == None:
			await ctx.send("Вы не ввели аргумент!", delete_after=10)
		elif arg not in ["msg", "lvl"]:
			await ctx.send("введен неопознанный аргумент!", delete_after=10)
		else:
			db = Connect.conn()
			curs = db.cursor()
			curs.execute(f"SELECT * FROM users ORDER BY {arg} DESC LIMIT 0, 10")
			res = curs.fetchall()
			db.close()
			arged = 2 if arg == "lvl" else 3
			arged2 = "levels" if arg == "lvl" else "msg's"
			embed = discord.Embed(title="TOP", colour=0x020202)
			for i in res:
				try:
					usr = self.bot.get_user(int(i[0]))
					embed.add_field(name=f"{usr.name}", value=f"{i[arged]} {arged2}", inline=False)
				except Exception:
					pass

			await ctx.send(embed=embed, delete_after=10)
	@commands.command()
	async def my(self, ctx):
		"""Выводит информацию о вас"""
		await ctx.message.delete()
		db = Connect.conn()
		curs = db.cursor()
		embed= discord.Embed(title= "Ваша статистика", colour= 0x020202)
		curs.execute(f"SELECT * FROM users WHERE id={ctx.author.id}")
		res = curs.fetchall()[0]
		procentOne = 1000+100*res[2]
		procentOne = round(procentOne/100)
		procentXp = round(res[1]/procentOne)
		progressbar = ""
		for i in range(round(procentXp/5)):
			progressbar = progressbar +"█"
		for i in range(20 - round(procentXp/5)):
			progressbar = progressbar + "--"
		embed.add_field(name="xp", value=f"{procentXp}%\\100%", inline=False)
		embed.add_field(name="progressbar", value=f"{progressbar}")
		embed.add_field(name="lvl", value=f"{res[2]}", inline=False)
		embed.add_field(name="msg's", value=f"{res[3]}", inline=False)
		db.close()
		try:
				await ctx.author.send(embed=embed)
		except Exception:
			await ctx.send(f"{ctx.author.mention} Так как у тебя выключен лс, напишу тут.", embed= embed, delete_after=15)

def setup(bot):
	bot.add_cog(Rank(bot))
	print("[INFO] Ranked loaded")
