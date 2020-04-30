import discord
from discord.ext import commands
import asyncio
from bs4 import BeautifulSoup as bs
import requests
import re

class VkParse(commands.Cog):
	def __init__(self, Bot):
		self.Bot = Bot
		self.loop = Bot.loop
		self.url = "https://vk.com/" # ссылка на группу
		self.pinged = True # если есть закреп = True
		self.lastPostId = None
		self.chat_id = # канал для уведомлений

	async def vk(self):
		channel = self.Bot.get_channel(self.chat_id)
		try:
			s = requests.Session()
			res = s.get(self.url).content
			s.close()
		finally:
			s.close()
		group = bs(res, 'html.parser')
		r = group.find_all('div', class_="wall_item")[1 if self.pinged else 0]
		postid = r.find('a', class_="anchor").get('name')
		self.lastPostId = postid
		while self.Bot.is_ready():
			try:
				s = requests.Session()
				res = s.get(self.url).content
				s.close()
			finally:
				s.close()
			group = bs(res, 'html.parser')
			r = group.find_all('div', class_="wall_item")[1 if self.pinged else 0]
			postid = r.find('a', class_="anchor").get('name')
			if postid != self.lastPostId:
				desc = ""
				self.lastPostId = postid
				date = r.find('a', class_='wi_date').get('href')
				date = date[1::]
				title = "Ссылка на пост"
				try:
					desc = r.find('div', class_="pi_text").text
				except Exception as e:
					pass
				desc = desc.replace("<br/>", "\n")
				imgs = []
				try:
					r_imgs = r.find_all('div', class_="thumb_map_img thumb_map_img_as_div")
					print(r_imgs)
					for i in r_imgs:
						j = str(i['style'])
						print(j)
						j = j.split(";")
						if j[1] != '':
							j = j[1] + j[2]
						else:
							j = j[0]
						j = j.strip('background-image: url(')
						j = j.strip(');')
						imgs.append(j)

				except Exception as e:
					print(e)
					pass
				embed = discord.Embed(title=title, description=desc, colour=0x7766ff, url=f'{self.url}?w={date}%2Fall')
				if len(imgs) == 1:
					embed.set_image(url=f"{imgs[0]}")

				await channel.send(embed=embed)

				if len(imgs) > 1:
					for i in range(len(imgs)):
						imgEmb = discord.Embed(title=f"{i+1}-ое прикрепленное изоброжение", colour=0x7766ff)
						imgEmb.set_image(url=f"{imgs[i]}")
						await channel.send(embed=imgEmb)

			await asyncio.sleep(10)

	@commands.Cog.listener()
	async def on_ready(self):
		self.Bot.loop.create_task(self.vk())

def setup(bot):
	bot.add_cog(VkParse(bot))

	
