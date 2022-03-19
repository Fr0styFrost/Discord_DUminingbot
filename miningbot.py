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

#init DB object
#DB = DatabaseLayer(dDBInfo)




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

@bot.command()
async def testdb(ctx, arg1):

  Arg1upper = arg1.upper()
  if Arg1upper in UnitList:
    await ctx.send(DB.getUnitInfo(arg1))



class DatabaseLayer:

    #constructor
    def init(self, dDBInfo):
        self.cursor=none
        self.connection=none
        connect(self, dDBInfo)

    #function to connect db
    def connect(self, dDBInfo):
        try:
            self.connection = mysql.connector.connect(dDBInfo.get(host),
                                         dDBInfo.get(database),
                                         dDBInfo.get(user),
                                         dDBInfo.get(password))

            if self.connection.is_connected():
                db_Info = self.connection.get_server_info()
                print('Connected to MySQL Server version ', db_Info)
                self.cursor = self.connection.cursor()
                self.cursor.execute('select database();')
                record = self.cursor.fetchone()
                print('Connected to database: ', record)

        except Error as e:
            print('Error while connecting to MySQL', e)

    #function to disconnect db
    def disconnect(self):
        if self.connection.is_connected():
                        self.cursor.close()
                        self.connection.close()
                        print('MySQL connection is closed')

    #QUERY-functions

    #query to get info of single mining unit
    def getUnitInfo(self, mu_name):
        sqlcommand = 'SELECT * FROM miningunits WHERE name = ?'
        self.cursor.execute(sqlcommand, mu_name)
	row=cursor.fetchone()
	while (row!=None):
            returnList.add(row)
  	    row = cursor.fetchone()
        
        return returnList.add
	

    #query to get info of all mining units
    def getAllUnitInfo(self, mu_name):
        sqlcommand = 'SELECT * FROM miningunits'
        self.cursor.execute(sqlcommand)
	row=cursor.fetchone()
	while (row!=None):
            returnList.add(row)
  	    row = cursor.fetchone()

        return returnList.add

bot.run(os.getenv('TOKEN'))
