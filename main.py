import discord
import random
import firebase_admin
from firebase_admin import credentials, firestore
import asyncio

# ========= For Firestore (rev lead) ========= #

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

path_to_json = "" # enter path to json certificate here to read and write to Firestore
cred = credentials.Certificate(path_to_json)
firebase_admin.initialize_app(cred)

db = firestore.client()

# ========= Global variables (aka hardcoded data aka dumb) ========= #

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable"]

bad_words = ["shucks", "darn", "dang", "heck", "stupid", "dumb"]

starter_encouragements = [
  "Cheer up!",
  "Hang in there.",
  "You are a great person!",
  "You got this."
]

penalties = [10,25,85,100]
penaltiesDict = {10:"That's how many miles of gas you can save by using EVs!", 25:"That's how many minutes it takes to charge a certain percentage.", 85:"That's the percentage of EVs clean energy rate!", 100:" That's almost as many charging stations in Arkansa"}
valuesDict = {0:" <:evcar:812739608709431327> ", 1:"    ", 2:" <:rEVcoin:812771947054235678> ", 3:"  :construction:  "}

# Custom emotes
evcar = "  <:evcar:812739608709431327>  "
revcoin = "  <:rEVcoin:812771947054235678>  "

# ========= Rev help functions ========= #

def revhelp():
  embedVar = discord.Embed(title=":zap: List of rEVBot Features", description="Check out what features rEVBot has and what commands you can use!", color=0xFF7F50)
  embedVar.add_field(name=":video_game: rEV Minigame", value="`rev up`: Dodge obstacles and collect rEVcoins! <:rEVcoin:812771947054235678>", inline=False)
  embedVar.add_field(name=":coin: Your Balance", value="`rev bal`: Check your rEVcoin balance with this command! :coin:", inline=False)
  embedVar.add_field(name=":medal: Server Leaderboard", value="`rev lead`: See the richest rEVcoin users in your server! :trophy:", inline=False)
  embedVar.add_field(name=":desktop: Safe Space Feature", value="rEVBot servers are safe places. If you send a mean message, you'll lose <:rEVcoin:812771947054235678>!", inline=False)
  return embedVar

# ========= Rev bal functions ========= #

def get_bal_embed(user):
  embedVar = discord.Embed(title=f":zap: {user.name}'s rEVcoin Balance <:evcar:812739608709431327>", description=f"{user.mention} - Earn more by playing rEV UP with the `rev up` command!", color=0xFFFF00)
  embedVar.add_field(name="Your Balance:", value="**"+str(getCoins(user))+"**<:rEVcoin:812771947054235678>", inline=False)
  return embedVar

# ========= Rev lead functions ========= #

def getCoins(user):
  doc_ref = db.collection(u'coin leaderboard').document(u'{}'.format(user.id))
  get_bal= doc_ref.get({u'balance'}).to_dict()
  if get_bal is not None:
    bal = get_bal.get('balance')
    return bal
  return 0

def setCoins(user, new_bal):
  if user.bot == False:
    doc_ref = db.collection(u'coin leaderboard').document(u'{}'.format(user.id))
    if new_bal >= 0:
      doc_ref.set({
        u'balance':new_bal,
      })
    else:
      doc_ref.set({
        u'balance':0,
      })

def create_leaderboard(guild): # def function to create and return embed
  limit = 10
  embedVar = discord.Embed(title="", description="",color=0x00FFFF)
  index = 0
  lead_list=""
  membs =[]
  for mem in guild.members:
    num_of_coins = getCoins(mem)
    if num_of_coins!=0:
      membs.append((mem.name, num_of_coins))
  membs.sort(key=lambda x: x[1],reverse=True)
  for mem in membs:
    index +=1
    if index > limit:
      break
    if index == 1:
      lead_list += ":first_place:"
    elif index == 2:
      lead_list += ":second_place:"
    elif index == 3:
      lead_list += ":third_place:"
    else:
      lead_list += ":small_blue_diamond:"
    lead_list += " **"+str(mem[1])+"** - "+mem[0]+"\n"
  if lead_list=="":
    lead_list = "There are no active rEVBot players on this server :( To get more coins, play `rev up` to gain more!"
  embedVar.add_field(name=":zap:<:rEVcoin:812771947054235678>"+guild.name+"'s rEVcoin Leaderboard <:rEVcoin:812771947054235678>:zap:", value=lead_list, inline=False)
  return embedVar

# ========= Rev up functions ========= #

def matrixToString(game_matrix):
  gameval = ""
  for i in range(7):
    add = "|"+game_matrix[i][0]+"|"+game_matrix[i][1]+"|"+game_matrix[i][2]+"|\n"
    gameval += add
  gameval += "\n_"
  return gameval

def updateGame(carLocation, game_matrix):

  # returns number of coins gained, if -1 then hit obstacles
  coinsGained = 0
  if (game_matrix[5][carLocation]==valuesDict[2]):
    coinsGained = 2
  elif (game_matrix[5][carLocation]==valuesDict[3]):
    coinsGained = -1 #deal with hit obstacle some other way later

  # update matrix
  for i in range(6,-1,-1):
    game_matrix[i] = game_matrix[i-1]

  if (game_matrix[1][0]==valuesDict[1]) & (game_matrix[1][1]==valuesDict[1]) & (game_matrix[1][2]==valuesDict[1]) & (game_matrix[2][0]==valuesDict[1]) & (game_matrix[2][1]==valuesDict[1]) & (game_matrix[2][2]==valuesDict[1]):
    randomIndexes = [random.randint(1,3),random.randint(1,3),random.randint(1,3)]
    if (randomIndexes[0]==3) & (randomIndexes[1]==3) & (randomIndexes[2]==3):
      randomIndexes[random.randint(0,2)] = random.randint(1,2)
    game_matrix[0] = [valuesDict[randomIndexes[0]], valuesDict[randomIndexes[1]],valuesDict[randomIndexes[2]]]
  else:
    game_matrix[0] = [valuesDict[1], valuesDict[1], valuesDict[1]]
  game_matrix[6][carLocation] = valuesDict[0]

  return coinsGained

def newGameMatrix():

  # index 5, 3, 1
  game = [[],[valuesDict[1], valuesDict[1], valuesDict[1]],[valuesDict[1], valuesDict[1], valuesDict[1]],[],[valuesDict[1], valuesDict[1], valuesDict[1]],[valuesDict[1], valuesDict[1], valuesDict[1]],[valuesDict[1], valuesDict[0], valuesDict[1]]]

  randomIndexes = [random.randint(1, 3), random.randint(1, 3), random.randint(1, 3)]
  if (randomIndexes[0] == 3) & (randomIndexes[1] == 3) & (randomIndexes[2] == 3):
    randomIndexes[random.randint(0, 2)] = random.randint(1, 2)
  game[0] = [valuesDict[randomIndexes[0]], valuesDict[randomIndexes[1]],valuesDict[randomIndexes[2]]]

  randomIndexes = [random.randint(1, 3), random.randint(1, 3), random.randint(1, 3)]
  if (randomIndexes[0] == 3) & (randomIndexes[1] == 3) & (randomIndexes[2] == 3):
    randomIndexes[random.randint(0, 2)] = random.randint(1, 2)
  game[3] = [valuesDict[randomIndexes[0]], valuesDict[randomIndexes[1]], valuesDict[randomIndexes[2]]]

  return game


def hit_obstacle():
  # Found from https://www.bmw.com/en/innovation/electric-car-facts.html
  # https://www.gm.com/electric-vehicles.html
  quiz_questions = [
  ("Which country has the largest electric car market with over 1.2 million units sold in 2019","China"),
  ("Which car company has vowed to launch 30 electric vehicles around the world by 2025?", "General Motors"),
  ("Which country gets 100 percent of it's electricity from clean, green hydroelectric power?", "Albania"),
  ("Which Scandanavian country has the most new percentage of electic cars sold worldwide? (55 percent)", "Norway"),
  ("Which country has the greatest number of charging stations per person, over 37,000 public charging stations total?","Netherlands")
]
  chosen = random.choice(quiz_questions)
  return chosen

async def delayFifteen():
  await asyncio.sleep(15)

async def wait_for_answer(player, channel, points, delayTF):
  q_n_a = hit_obstacle()
  sent_question = await channel.send(content = player.mention + " - " + q_n_a[0] )
  try:
    msg = await client.wait_for('message', check=lambda message: message.author == player, timeout=15)
    if q_n_a[1].lower() in msg.content.lower():
      await sent_question.delete()
      await msg.delete()
      points[0]+=1
      return False
    else:
      setCoins(player, getCoins(player)+points[0])
      await channel.send(content = "That's the wrong answer :( The right answer was: **"+q_n_a[1]+"**. Better luck next time!")
      await asyncio.sleep(2)
      await channel.send(content = " Game over, your collected coins (**" +str(points[0])+"**<:rEVcoin:812771947054235678>) have been added to your account")

  except asyncio.exceptions.TimeoutError:
    setCoins(player, getCoins(player)+points[0])
    await channel.send(content = "You didn't answer in time :( The right answer was: **"+q_n_a[1]+"**. Better luck next time!")
    await asyncio.sleep(2)
    await channel.send(content = "Your collected coins (**" +str(points[0])+"**<:rEVcoin:812771947054235678>) have been added to your account")
  return True

async def create_game_frame(player, points, direction, game_matrix, channel, delayTF):
  em_space = " "
  en_space = " "
  embedVar = discord.Embed(title=":zap: rEV UP: The Minigame", description="Use the :arrow_left: and :arrow_right: reactions to control the car", color=0x00ff00)

  game_value = ""

  if direction == -1:
    add = updateGame(0, game_matrix)
    if add == -1:
      game_value = "You hit an obstacle :( answer this question in the next 15 sec to keep playing"
      delayTF[0] = await wait_for_answer(player, channel, points, delayTF)

    else:
      points[0] += add
      game_value = matrixToString(game_matrix)
  elif direction == 0:
    add = updateGame(1, game_matrix)
    if add == -1:
      game_value = "You hit an obstacle :( answer this question in the next 15 sec to keep playing"
      delayTF[0] = await wait_for_answer(player, channel, points, delayTF)
    else:
      points[0] += add
      game_value = matrixToString(game_matrix)
  elif direction == 1:
    add = updateGame(2, game_matrix)
    if add == -1:
      game_value = "You hit an obstacle :( answer this question in the next 15 sec to keep playing"
      delayTF[0] = await wait_for_answer(player, channel, points, delayTF)
    else:
      points[0] += add
      game_value = matrixToString(game_matrix)
  else:
    game_value = "You veered off the road x.X"
    setCoins(player, getCoins(player)+points[0])
    await channel.send(content = "You veered off the road :( Game over, your collected coins (**" +str(points[0])+"**<:rEVcoin:812771947054235678>) have been added to your account")
    delayTF[0] = True
  embedVar.add_field(name="Coins Collected:", value="**"+str(points[0])+"**<:rEVcoin:812771947054235678>", inline=False)
  embedVar.add_field(name=":traffic_light: Avoid the road obstacles and collect the rEVcoins!!", value=game_value, inline=False)
  return embedVar

def initializeMessage(game_matrix):
  embedVar = discord.Embed(title=":zap: rEV UP: The Minigame", description="Use the :arrow_left: and :arrow_right: reactions to control the car", color=0x00ff00)
  game_value = matrixToString(game_matrix)
  embedVar.add_field(name="Coins Collected:", value="**"+str(0)+"**<:rEVcoin:812771947054235678>", inline=False)
  embedVar.add_field(name=":traffic_light: Avoid the road obstacles and collect the rEVcoins!!", value=game_value, inline=False)
  return embedVar

def updateCarPosition(game_matrix, position):
  if position == -1:
    game_matrix[6][0] = valuesDict[0]
  elif position == 0:
    game_matrix[6][1] = valuesDict[0]
  else:
    game_matrix[6][2] = valuesDict[0]

async def loop_for_game(accept_decline, points, player, current, game_matrix, message, delayTF, count):
  every_sec = 2
  while delayTF[0] == False:
    reaction = None
    try:
      reaction, user = await client.wait_for('reaction_add', check=lambda r, u: u.id == player.id, timeout=0.1)
    except asyncio.exceptions.TimeoutError:
      if count%every_sec==0:
        await sendOrDelay(player, points, current, game_matrix, message, delayTF, accept_decline)
      count = round(count+0.1,1)
    if reaction==None:
      if count%every_sec==0:
        await sendOrDelay(player, points, current, game_matrix, message, delayTF, accept_decline)
    elif reaction.emoji == "⬅️":
      current-=1
      updateCarPosition(game_matrix, current)
      await reaction.remove(player)
      await sendOrDelay(player, points, current, game_matrix, message, delayTF, accept_decline)
    elif reaction.emoji == "➡️":
      current+=1
      updateCarPosition(game_matrix, current)
      await reaction.remove(player)
      await sendOrDelay(player, points, current, game_matrix, message, delayTF, accept_decline)
    count = round(count+0.1,1)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    # Setting `Playing ` status
    await client.change_presence(activity=discord.Game(name="rev help"))

async def sendOrDelay(player, points, current, game_matrix, message, delayTF, accept_decline):
  embedVar = create_game_frame(player, points, current, game_matrix, message.channel, delayTF)
  if delayTF[0]:
    delayTF[0] = False
  await accept_decline.edit(embed=await embedVar)

async def end_task(task):
  await asyncio.sleep(5)
  task.cancel()

# ========= Main program ========= #

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    msg = message.content.lower()

    if any(word in msg for word in sad_words):
      await message.reply(random.choice(starter_encouragements))

    if any(word in msg for word in bad_words):
      points_lost = random.choice(penalties)
      await message.reply("You have lost "+str(points_lost)+" <:rEVcoin:812771947054235678>. Fun fact: "+penaltiesDict[points_lost])
      setCoins(message.author, getCoins(message.author)-points_lost)
      
    if msg.startswith('rev '):
      if msg.startswith('rev up'):
        player = message.author
        if player.bot == False:
          current = 0
          points = [0]
          #initial game matrix
          game_matrix = newGameMatrix()
          game_message = initializeMessage(game_matrix)
          accept_decline = await message.channel.send(embed=game_message)
          await accept_decline.add_reaction("⬅️")
          await accept_decline.add_reaction("➡️")

        delayTF = [False]
        count = 0.1
        client.loop.create_task(loop_for_game(accept_decline, points, player, current, game_matrix, message, delayTF, count))

      elif msg.startswith('rev lead'):
        game_message = create_leaderboard(message.guild)
        await message.channel.send(embed=game_message)
        # Check if user has reacted, if so move the car to the left

      elif msg.startswith('rev help'):
        game_message = revhelp()
        await message.channel.send(embed=game_message)

      elif msg.startswith('rev bal'):
        game_message = get_bal_embed(message.author)
        await message.channel.send(embed=game_message)
        
    if 'country roads' in msg:
      await message.reply('Take me home.')
      
client.run('') # Enter token here
