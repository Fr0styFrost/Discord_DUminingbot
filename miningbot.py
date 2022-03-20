import discord
import os
import re
import time
import urllib.parse as urlparse
from discord.ext import commands
import mysql.connector
from mysql.connector import Error

#get DB info from ENV_Var
url = urlparse.urlparse(os.environ['DATABASE_URL'])

#dict. for database inf storage
dDBInfo = {
    'host' : url.hostname,
    'dbname' : url.path[1:],
    'user' : url.username,
    'password' : url.password,
    'port' : url.port
}

class DBhandler:
    #all returns of queries are list of tuples [(x,y,z),(x,y,z)]
    #constructor
    def __init__(self, dbinfo):
        self.cursor=None
        self.connection=None
        self.connect(dDBInfo)
        
    #connect db
    def connect(self, dbinfo):
        try:
            self.connection = psycopg2.connect(host = dbinfo.get(host),
                                         dbname = dbinfo.get(dbname),
                                         user = dbinfo.get(user),
                                         password = dbinfo.get(password),
                                         port = dbinfo.get(port))
            # Create a cursor to perform database operations
            self.cursor = connection.cursor()
            print("PostgreSQL server information:")
            print(connection.get_dsn_parameters(), "\n")
            
            # Executing a SQL query
            self.cursor.execute("SELECT version();")
            # Fetch result
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")
            
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)
            
    #disconnect db
    def disconnect(self):
        if (connection):
            self.cursor.close()
            self.connection.close()
            print("PostgreSQL connection is closed")
    
    #--------MINING UNIT COMMANDS--------
    #initial unit-read function
    def initUnitList(self):
        query='SELECT muname FROM miningunits'
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows
    
    #get Info of single unit
    def getUnitInfo(self,muname):
        query='SELECT * FROM miningunits WHERE muname = %s'
        self.cursor.execute(query,muname)
        rows = self.cursor.fetchall()
        return rows
    
    #get Info of all units
    def getAllUnitInfo(self):
        query='SELECT * FROM miningunits'
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows
    
    #Update Info of single unit
    def updateUnit(self,muname,calib,unixstring):
        query='UPDATE miningunits SET calibration = %s, timeleft = %s WHERE muname = %s'
        self.cursor.execute(query,[calib, unixstring, muname])
        
    #Add new unit
    def addUnit(self,muname,calib,unixstring):
        query='INSERT INTO miningunits VALUES(muname=%s, calibration=%s, timeleft=%s)'
        self.cursor.execute(query,[muname, calib, unixstring])
        
    #remove unit
    def deleteUnit(self,muname):
        query='DELETE FROM miningunits WHERE muname=%s)'
        self.cursor.execute(query,[muname])
        
    #--------PAYMENT TABLE COMMANDS--------
    #get Info of player
    def getPlayerPayment(self,playername):
        query='SELECT * FROM payment WHERE playername = %s'
        self.cursor.execute(query,[playername])
        rows = self.cursor.fetchall()
        return rows
    
    #get Info of all players
    def getAllPayment(self):
        query='SELECT * FROM payment'
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows
    
    #Add player payment
    def addPayment(self,playername):
        query='UPDATE payment SET calibcount = calibcount +1, payment = payment + payment WHERE playername = %s'
        self.cursor.execute(query,[playername])
    
    #clear player payment
    def clearPayment(self,playername):
        query='UPDATE payment SET calibcount = 0, payment = 0 WHERE playername = %s'
        self.cursor.execute(query,[playername])
    
    #--------HEX RENTAL COMMANDS--------
    #get Info of specific player rentals
    def getPlayerHexRentals(self,playername):
        query='SELECT * FROM hexrental WHERE playername = %s'
        self.cursor.execute(query,[playername])
        rows = self.cursor.fetchall()
        return rows
    
    #get Info of all players rentals
    def getAllHexRentals(self):
        query='SELECT * FROM hexrental'
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows
    
    #update hex rental
    def updateHexRental(self,hexname,playername,duedate):
        query='UPDATE hexrental SET duedate = %s WHERE playername = %s AND hex = %s'
        self.cursor.execute(query,[duedate, playername, hexname])
        
    #add new hex rental
    def addHexRental(self,hexname,playername,duedate):
        query='INSERT INTO hexrental VALUES(hex=%s, playername=%s, duedate=%s)'
        self.cursor.execute(query,[hexname, playername, duedate])
        
    #clear hex rental
    def clearHexRental(self,hexname):
        query='DELETE FROM hexrental WHERE hex=%s)'
        self.cursor.execute(query,[hexname])
   
#create DB object
DB = DBhandler(dDBInfo)

#create bot object
bot = commands.Bot(command_prefix='!')

#initial filling of mining unit List:
result = DB.initUnitList()
for entry in result:
    UnitList.append(entry[0])

#--------generic bot commands--------
@bot.command()
async def help(ctx):
    #display available commands
    pass
    
#--------mining unit bot commands--------

#get specific mining unit info
@bot.command()
async def getUnit(ctx, muname):
    #check input
    muname = muname.upper()
    if muname in UnitList:
        result = DB.getUnitInfo(muname)
        calTime = '<t:' + entry[2] + ':R>'
        await ctx.send('Name: {} , Calibration needed in {}'.format(entry[0],calTime))

#get all mining unit info
@bot.command()
async def getAllUnits(ctx):
    result = DB.getAllUnitInfo()
    for entry in result:
        calTime = '<t:' + entry[2] + ':R>'
        await ctx.send('Name: {} , Calibration needed in {}'.format(entry[0],calTime))

#calibrate mining unit
@bot.command()
async def calib(ctx, muname, calibration):
    #check inputs
    muname = muname.upper()
    calibration = calibration[:-1]
    reResult = re.match('^[1-9][0-9]?$|^100$', calibration)
    
    if muname in UnitList and reResult:
        #unix calculation
        percentage = int(calibration) 
        UTime = str(int(((percentage - 65)/0.625+72)*3600 + time.time()))
        calTime = '<t:' + UTime + ':R>'
        #updating mining units table
        DB.updateUnit(muname, percentage, UTime)
        await ctx.send('You updated {} to {}% and will need recalibration in {}'.format(muname, percentage, calTime))
        #updating payments table
        userName = ctx.message.author.mention
        #DB.addPayment(userName) #her name needs to inserted
        await ctx.send('Added 1 Calibration and 200k to your payment for calibrating {}'.format(muname))
    else:
        await ctx.send('Input arguments were not correct!(MiningUnit not found or calibration out of range)')
        

bot.run(os.getenv('DISCORD_TOKEN'))
