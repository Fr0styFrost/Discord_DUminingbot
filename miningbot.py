import discord
import os
import re
import time
from discord.ext import commands
import mysql.connector
from mysql.connector import Error

dDBInfo = {
    'host' : '',
    'database': '',
    'user': '',
    'password': ''
}

bot = commands.Bot(command_prefix='!')

@bot.command()
async def cal(ctx, arg1, arg2):

  UnitList = ["MU1-1", "MU1-2", "MU2-1", "MU2-2"]
  Arg1upper = arg1.upper()
  input2 = arg2
  input2 = input2[:-1]
  arg2result = re.match('^[1-9][0-9]?$|^100$', input2)
  
  
  if Arg1upper in UnitList and arg2result:
    per = int(input2)
    UTime = str(int(((per - 65)/0.625+72)*3600 + time.time())) #Unix timer calculation
    calTime = '<t:' + UTime + ':R>' #Discord timer command
           #its in correct range
    await ctx.send('You calibrated {} to {}% and will need recalibration in {}'.format(Arg1upper, per, calTime))
  else:
      await ctx.send(Arg1upper)
      await ctx.send(arg2result)
      
      #its not in correct range

bot.run(os.getenv('DISCORD_TOKEN'))
