import discord
import os
import re
import time
import urllib.parse as urlparse
from discord.ext import commands
import psycopg2

#get DB info from ENV_Var
DATABASE_URL = os.environ['DATABASE_URL']

class DBhandler:
    #all returns of queries are list of tuples [(x,y,z),(x,y,z)]
    #constructor
    def __init__(self, DATABASE_URL):
        self.cursor=None
        self.connection=None
        self.connect(DATABASE_URL)
        
    #connect db
    def connect(self, DATABASE_URL):
        try:
            self.connection = psycopg2.connect(DATABASE_URL, sslmode='require')

            # Create a cursor to perform database operations
            self.cursor = self.connection.cursor()
            print("PostgreSQL server information:")
            print(self.connection.get_dsn_parameters(), "\n")
            
            # Executing a SQL query
            self.cursor.execute("SELECT version();")
            # Fetch result
            record = self.cursor.fetchone()
            print("You are connected to - ", record, "\n")
            
        except psycopg2.Error as e:
            print("Error while connecting to PostgreSQL", e.pgerror)
            
    #disconnect db
    def disconnect(self):
        if (self.connection):
            self.cursor.close()
            self.connection.close()
            print("PostgreSQL connection is closed")
    
    #--------MINING UNIT COMMANDS--------
    #initial unit-read function
    def initUnitList(self):
        query='''SELECT "miningunits"."muname" FROM "miningunits"'''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows
    
    #get Info of single unit
    def getUnitInfo(self,muname):
        query='''SELECT * FROM "miningunits" WHERE "miningunits"."muname" = %s'''
        self.cursor.execute(query,(muname,))
        rows = self.cursor.fetchall()
        return rows
    
    #get Info of all units
    def getAllUnitInfo(self):
        query='''SELECT * FROM "miningunits" ORDER BY "timeleft" DESC'''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows
    
    #Update Info of single unit
    def updateUnit(self,muname,calib,unixstring):
        query='''UPDATE "miningunits" SET "calibration" = %s, "timeleft" = %s WHERE "miningunits"."muname" = %s'''
        self.cursor.execute(query,(calib, unixstring, muname,))
        self.connection.commit()
        
    #Add new unit
    def addUnit(self,muname,calib,unixstring):
        query='''INSERT INTO "miningunits" ("muname", "calibration", "timeleft") VALUES (%s, %s, %s)'''
        self.cursor.execute(query,(muname, calib, unixstring,))
        self.connection.commit()
        
    #remove unit
    def deleteUnit(self,muname):
        query='''DELETE FROM "miningunits" WHERE "miningunits"."muname"=%s)'''
        self.cursor.execute(query,(muname,))
        self.connection.commit()
        
    #--------PAYMENT TABLE COMMANDS--------
    #get Info of player
    def getPlayerPayment(self,playername):
        query='''SELECT * FROM "payment" WHERE "payment"."playername" = %s'''
        self.cursor.execute(query,(playername,))
        rows = self.cursor.fetchall()
        return rows
    
    #get Info of all players
    def getAllPayment(self):
        query='''SELECT * FROM "payment"'''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows
    
    #Add player payment
    def addPayment(self,playername):
        #check if player already in DB
        checkquery='''SELECT * FROM "payment" WHERE "payment"."playername" = %s'''
        self.cursor.execute(checkquery,(playername,))
        rows = self.cursor.fetchall()
        if rows:
            #player already in db - update his entry
            query='''UPDATE "payment" SET "calibcount" = "calibcount" + 1, "payment" = "payment" + 250000 WHERE "payment"."playername" = %s'''
            self.cursor.execute(query,(playername,))
            self.connection.commit()
        else:
            #player is not in db - create new entry
            query='''INSERT INTO "payment" ("playername", "calibcount" ,"payment") VALUES(%s, %s, %s)'''
            self.cursor.execute(query,(playername,"1","250000",))
            self.connection.commit()
            
    #clear player payment
    def clearPayment(self,playername):
        query='''UPDATE "payment" SET "calibcount"  = 0, "payment" = 0 WHERE "payment"."playername" = %s'''
        self.cursor.execute(query,(playername,))
        self.connection.commit()
        
    #--------HEX RENTAL COMMANDS--------
    #get Info of specific player rentals
    def getPlayerHexRentals(self,playername):
        query='''SELECT * FROM "hexrental" WHERE "hexrental"."playername" = %s'''
        self.cursor.execute(query,(playername,))
        rows = self.cursor.fetchall()
        return rows
    
    #get Info of all players rentals
    def getAllHexRentals(self):
        query='''SELECT * FROM "hexrental"'''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows
    
    #update hex rental
    def updateHexRental(self,hexname,playername,duedate):
        query='''UPDATE "hexrental" SET "duedate" = %s WHERE "hexrental"."playername" = %s AND "hexrental"."hex" = %s'''
        self.cursor.execute(query,(duedate, playername, hexname,))
        self.connection.commit()
        
    #add new hex rental
    def addHexRental(self,hexname,playername,duedate):
        query='''INSERT INTO "hexrental" ("hex", "playername", "duedate") VALUES(%s, %s, %s)'''
        self.cursor.execute(query,(hexname, playername, duedate,))
        self.connection.commit()
        
    #clear hex rental
    def clearHexRental(self,hexname):
        query='''DELETE FROM "hexrental" WHERE "hexrental"."hex"=%s)'''
        self.cursor.execute(query,(hexname,))
        self.connection.commit()
   
#create DB object
DB = DBhandler(DATABASE_URL)

#create bot object
bot = commands.Bot(command_prefix='!')

#initial filling of mining unit List:
UnitList=[]
result = DB.initUnitList()
for entry in result:
    UnitList.append(entry[0])


#--------mining unit bot commands--------
#get specific mining unit info
@bot.command()
async def getUnit(ctx, muname):
    #check input
    muname = muname.upper()
    if muname in UnitList:
        result = DB.getUnitInfo(muname)
        calTime = '<t:' + result[0][2] + ':R>'
        await ctx.send('Name: {} , Calibration needed in {}'.format(result[0][0],calTime))
    else:
        await ctx.send('Input arguments were not correct!(MiningUnit not found!)')
        
#get all mining unit info
@bot.command()
async def getAllUnits(ctx):
    result = DB.getAllUnitInfo()
    mulist = []
    for entry in result:
        calTime = '<t:' + entry[2] + ':R>'
        mulist.append('Name: {} , Calibration needed in {}'.format(entry[0],calTime))
    n = 10
    l=[mulist[i:i+n] for i in range(0, len(mulist), n)]
    for el in l:
        await ctx.send('\n'.join(el))
        

#calibrate mining unit
@bot.command()
async def calib(ctx, muname, calibration):
    #check inputs
    muname = muname.upper()
    if "%" in calibration:
        calibration = calibration[:-1]
    reResult = re.match('^[1-9][0-9]?$|^100$', calibration)
    
    if muname in UnitList and reResult:
        #check old Data
        if muname in UnitList:
            result = DB.getUnitInfo(muname)
            oldtime = int(result[0][2])
        if oldtime > 86400 + time.time():
            await ctx.send('This unit did not need calibration. You have wasted your charge. No payment will be made for this calibration.')
        else:
            #unix calculation
            percentage = int(calibration) 
            UTime = str(int(((percentage - 65)/0.625+72)*3600 + time.time()))
            calTime = '<t:' + UTime + ':R>'
            #updating mining units table
            DB.updateUnit(muname, percentage, UTime)
            await ctx.send('You updated {} to {}% and will need recalibration in {}'.format(muname, percentage, calTime))
            #updating payments table
            userName = ctx.message.author.display_name
            print(userName)
            DB.addPayment(userName) #her name needs to inserted
            await ctx.send('{}, you added 1 Calibration and 250k to your payment for calibrating {}'.format(userName, muname))
    else:
        await ctx.send('Input arguments were not correct!(MiningUnit not found or calibration out of range)')

#--------payment bot commands--------

#--------Admin commands--------
#add Unit
#Delete Unit
#get specific payment info of player
@bot.command()
async def getAllPayment(ctx):
    role = discord.utils.get(ctx.guild.roles, id=952705796985208842)
    if role in ctx.author.roles:
        result = DB.getAllPayment()
        for entry in result:
            await ctx.send('Name: {} , Calibrations done: {}, Payment: {}'.format(entry[0], entry[1], entry[2]))
    else: 
        await ctx.send('You do not have access to this command.')

@bot.command()
async def addUnit(ctx,muname):
    role = discord.utils.get(ctx.guild.roles, id=952705796985208842)
    if role in ctx.author.roles:    
        muname = muname.upper()       
        if muname in UnitList:
            await ctx.send('This unit is already in the list')
        else: 
            calib = 0
            unixstring = int(time.time())               
            DB.addUnit(muname,calib,unixstring)
            UnitList.append(muname)
            await ctx.send('{} has been added.'.format(muname))
            
    else: 
        await ctx.send('You do not have access to this command.')
        
@bot.command()
async def clearPayment(ctx,playername):
    role = discord.utils.get(ctx.guild.roles, id=952705796985208842)
    if role in ctx.author.roles:        
        DB.clearPayment(playername)
        await ctx.send('{} has been paid.'.format(playername))
    else:
        await ctx.send('You do not have access to this command.')
    
@bot.command()
async def test(ctx):
     await ctx.send(UnitList)

bot.run(os.getenv('DISCORD_TOKEN'))
