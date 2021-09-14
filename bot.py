import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from database import Database

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix='`')
db = Database()

@client.event
async def on_ready():
    scan_wolt.start()
    print("Bot is ready")

@tasks.loop(seconds=60)
async def scan_wolt():
    status_name = {0: 'unavailable', 1: 'available'}
    for res in db.query('select * from restaurant'):
        link = res[2]
        status = check_status(link)
        if status != res[3]:
            db.query(f'update restaurant set last_status = {status} where id={res[0]}')
            for channel in db.query(f'select channel_id from channel_restaurant where restaurant_id={res[0]}'):
                channel = client.get_channel(int(channel[0]))
                await channel.send(f"{res[1]} status changed to **{status_name[status]}**")


@client.command(name='add')
async def add_restaurant(ctx, link = None):
    if not link:
        await ctx.send("Restaurant link required as argument")
        return
    
    name = link.split('/')[-1]
    # TODO check if valid wolt link
    status = check_status(link)
    restaurant = db.query(f'select * from restaurant where link = "{link}"').fetchone()
    
    if restaurant is not None:
        res_id = restaurant[0]
    else:
        name = link.split('/')[-1]
        status = check_status(link)
        db.query(f'insert into restaurant(name, link, last_status) values("{name}", "{link}", {status})')
        res_id = db.query('select max(id) from restaurant').fetchone()[0]
    
    dup_check = db.query(f'select * from channel_restaurant where channel_id="{ctx.message.channel.id}" and restaurant_id={res_id}').fetchone()
    if dup_check is None:
        db.query(f'insert into channel_restaurant(channel_id, restaurant_id) values("{ctx.message.channel.id}", {res_id})')
    else:
        await ctx.send(f"Updates for this restaurant are already being sent to this channel")
        return
    await ctx.send(f"Success, informing channel about changes in {name}")

def check_status(link):
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'html.parser')
    delivery = soup.find('button', class_ = 'DeliveryTypeButton-module__root___c0B1z Venue-module__headerButton___3zfqF')
    delivery = delivery.find('span', class_ = 'ContentButton-module__text___2PSlt')
    if delivery.text == "Schedule for later":
        return 0
    return 1


@client.command(name='remove')
async def remove_restaurant(ctx, name):
    restaurant = db.query(f'select id from restaurant where name = "{name}"').fetchone()
    if restaurant is None:
        await ctx.send("Could not find restaurant with name")
        return
    
    res_id = restaurant[0]
    chan_restaurant = db.query(f'select * from channel_restaurant where channel_id="{ctx.message.channel.id}" and restaurant_id={res_id}')
    if chan_restaurant is None:
        await ctx.send("Restaurant is not tracked in this channel")
        return

    db.query(f'delete from channel_restaurant where channel_id="{ctx.message.channel.id}" and restaurant_id={res_id}')
    await ctx.send("Removed successfully")

@client.command(name='list')
async def list_restaurants(ctx):
    embed=discord.Embed(
        title="Channel restaurants",
        description="Restaurant updates this channel is subscribed to",
        color=discord.Color.blue())
    rows = db.query(f'select restaurant_id from channel_restaurant where channel_id="{ctx.message.channel.id}"').fetchall()
    for row in rows:
        restaurant = db.query(f'select * from restaurant where id={row[0]}').fetchone()
        status = "✅ Available"
        if restaurant[3] == 0:
            status = "❌ Unavailable"
        embed.add_field(name=restaurant[1], value=f"[**{status}**]({restaurant[2]})", inline=False)
    await ctx.send(embed = embed)

client.run(TOKEN)
