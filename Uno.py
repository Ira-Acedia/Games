from tkinter import *
from time import sleep
from random import shuffle
from random import randint as random
from threading import Thread

# Initalise Window
rootCol = "lightgoldenrodyellow"
root = Tk(bg=rootCol)
windowWidth = (root.winfo_screenwidth() > 1350 and root.winfo_screenheight() > 850 and [1280, 1300]) or [1126, 1150]
windowHeight = (windowWidth[0] == 1280 and [720, 800]) or [634, 660]
root.geometry(f"{windowWidth[1]}x{windowHeight[1]}")
root.title("Uno")
root.resizable(False,False)

# Variables you can change
computerDelay = 1
fontSize = (windowWidth[0] == 1280 and 20) or 12
fontType = "Arial"
backgroundImage = (windowWidth[0] == 1280 and "Blue") or "S_Blue"
folder = "Uno_Assets"
cardsInDeck = {
    "Wilds": {"Wild": 4, "Wild_Draw": 4},
    "Normal": {"Blue": {"0": 1, "1": 2, "2": 2, "3": 2, "4": 2, "5": 2, "6": 2, "7":2, "8":2, "9": 2, "Skip": 2, "Draw": 2, "Reverse": 2},
    "Green": {"0": 1, "1": 2, "2": 2, "3": 2, "4": 2, "5": 2, "6": 2, "7":2, "8":2, "9": 2, "Skip": 2, "Draw": 2, "Reverse": 2},
    "Red": {"0": 1, "1": 2, "2": 2, "3": 2, "4": 2, "5": 2, "6": 2, "7":2, "8":2, "9": 2, "Skip": 2, "Draw": 2, "Reverse": 2},
    "Yellow": {"0": 1, "1": 2, "2": 2, "3": 2, "4": 2, "5": 2, "6": 2, "7":2, "8":2, "9": 2, "Skip": 2, "Draw": 2, "Reverse": 2}}
    }

# Irrelevant variables. Mostly.
cardsRemaining = []
fontInfo = (fontType, fontSize)
canvas = Canvas(root, width=windowWidth[0], height=windowHeight[0])
canvas.place(relx=0.5, rely=0.5, anchor=CENTER)
deck = None
lastPlayed = None
uno = False
reverse = False
Colour = "Red"
oldDiscardPile = []
playerCount = StringVar()
players = []
images = {"Red": PhotoImage(file=f"{folder}/Table_0.png"), # Dark Red
          "Purple": PhotoImage(file=f"{folder}/Table_1.png"), # Dark Purple
          "Green": PhotoImage(file=f"{folder}/Table_2.png"), # Dark Green
          "Blue": PhotoImage(file=f"{folder}/Table_3.png"), # Dark Blue
          "B_Green": PhotoImage(file=f"{folder}/Table_4.png"),  # Brighter Green
          "Back": PhotoImage(file=f"{folder}/Back.png"), # Back of card
          "Deck": PhotoImage(file=f"{folder}/Deck.png"), # Deck image (for drawing cards)
          "UNO": PhotoImage(file=f"{folder}/Logo.png"), # big sign
          "UNO_Button": PhotoImage(file=f"{folder}/UnoButton.png"),
          "S_Red": PhotoImage(file=f"{folder}/S_Table_0.png"), # Dark red for smaller resolutions
          "S_Purple": PhotoImage(file=f"{folder}/Table_1.png"),
          "S_Green": PhotoImage(file=f"{folder}/Table_2.png"),
          "S_Blue": PhotoImage(file=f"{folder}/Table_3.png"),
          "S_B_Green": PhotoImage(file=f"{folder}/Table_4.png")
          }

# If you're going to change background colour, you have to change these too.
pseudoBackground = "#40686A" # makes images "transparent" background
darkPseudoBack = "#1F3233" # for upper and lower areas

drawDeck = Label(canvas, image=images["Deck"], bg=pseudoBackground)

class Player():            
    def __init__(self, name, anch, x, y, isTurn, bot, scoreLabelPos):
        self.name = name
        self.hand = []
        self.score = 0 # 500 to win
        self.frame = Frame(canvas, width=59, height=84, bg=darkPseudoBack)
        self.ScoreLabel = Label(root, text=f"{name}: 0", font=fontInfo,bg=rootCol)
        self.ScoreLabel.place(relx=scoreLabelPos,anchor="n")        
        self.frame.place(relx=x, rely=y, anchor=anch)
        self.objects = []
        self.netObjs = []
        self.bot = bot
        self.turn = isTurn
        self.drawn = False # serves as a debounce
        self.lastDrawn = None
        players.append(self)
        if anch == "s" or anch == "n":
            self.side="H" # Horizontal
        else:
            self.side = "V" # Vertical
        self.draw(7)

    def restart(self, isTurn):
        for i in self.objects:
            i.destroy()
        self.hand = []
        self.objects = []
        self.netObjs = []
        self.turn = isTurn
        self.ScoreLabel["fg"] = "Black"
        self.drawn = False
        self.LastDrawn = None
        self.draw(7)
        
    def useCard(self, event, card):
        global lastPlayed, Colour, uno
        # why you trying to cheat fool
        if not self.turn or not Colour or not isValidCard(card):
            return

        # destroy used card from hand
        toBeDestroyed = [None, 0]
        for i in range(len(self.hand)):
            if self.hand[i] == card:
                self.hand.pop(i)
                toBeDestroyed = [self.objects[i], i]
                break

        for i in range(1, len(self.netObjs) + 1):
            i *= -1 # Reverse indexing to find "faster" during long games
            if self.netObjs[i] == toBeDestroyed[0]:
                toBeDestroyed[0].destroy()
                self.objects.pop(toBeDestroyed[1])
                break
        # Add card to discard pile, update hand
        oldDiscardPile.append(card)
        self.updateHand()
        usedPileCard = Label(canvas, image=images[card], bg=pseudoBackground)
        usedPileCard.place(relx=0.5, rely=0.5, anchor=CENTER)
        ColourChosen.place_forget()
        # give colour change option for wild card, make sure to change _Draw to _Colour
        viableWild = True
        if card.find("Wild") != -1:
            # checks if wild card draw 4 was legally played
            if card.find("Draw") != -1:
                for i in self.hand:
                    if i[:i.find("_")] == lastPlayed[:lastPlayed.find("_")]:
                        viableWild = False
                        break
                    
            if not self.bot:
                changeColour(None)
            else:
                # bot has to think card what colour he wants. :>
                appearances = {"Green": 0, "Blue": 0, "Red": 0, "Yellow": 0}
                for card in self.hand:
                    col = card[:card.find("_")]
                    try:
                        appearances[col] += 1
                    except:
                        pass
                mostAppeared = [None, 0]
                for i in appearances:
                    if appearances[i] >= mostAppeared[1]:
                        mostAppeared = [i, appearances[i]]
                changeColour(mostAppeared[0])
        else: # peasant card used
            lastPlayed = card

        # finished game wow
        if len(self.hand) == 0:
            gameOver(self)
            return
        elif len(self.hand) == 1: # check if player legally announced uno
            if uno:
                UnoSign.place(relx=0.5, rely=0.5, anchor=CENTER)
                root.after(500, lambda: UnoSign.place_forget())
            else:
                self.draw(2)

        uno = False

        # Let action cards work accordingly
        if card.find("Reverse") != -1:
            self.endTurn("Reverse")
        elif card.find("Skip") != -1:
            self.endTurn("Skip")
        elif card == "Wild_Draw" != -1:
            # check viable
            if viableWild:
                self.endTurn("Draw_4")
            else:
                self.draw(4)
                self.endTurn(None)
        elif card.find("Draw") != -1:
            self.endTurn("Draw_2")
        else:
            self.endTurn(None)

    def updateHand(self):
        # Visual representation of cards in hands
        if self.side == "H": # Horizontal
            self.frame["width"] = len(self.objects)*59 # 58 + 1
        else:
            self.frame["height"] = len(self.objects)*84 # 84 + 1
        i = 1
        for obj in self.objects:
            if self.side == "H":
                obj.place(relx=i/len(self.objects), rely=0, anchor="ne")
            else:
                obj.place(relx=0,rely=i/len(self.objects), anchor="sw")
            i += 1
            root.update()
            
    def add(self, card):
        # Add card to hand
        self.objects.append(Label(self.frame, anchor="nw", image=images[card], bg=darkPseudoBack))
        self.netObjs.append(self.objects[-1])
        if not self.bot:
            self.objects[-1].bind("<Button-1>", lambda e: self.useCard(e, card))
        self.updateHand()
            
    def draw(self, amount):
        global deck, oldDiscardPile
        try:
            # Draw x amount of cards
            for i in range(amount):
                self.hand.append(deck[0])
                self.lastDrawn = deck[0]
                if self.bot: self.add("Back")
                else: self.add(deck[0])
                deck.pop(0)
                sleep(0.1)
        except Exception as e:
            # oh no! Ran out of cards. Reset deck with used cards.
            deck = oldDiscardPile
            shuffle(deck)
            oldDiscardPile = []
            self.draw(amount)

    def handWorth(self):
        # Get hand worth for end of game scoring
        points = 0
        for card in self.hand:
            if card.find("Wild") > -1:
                points += 50
            elif card.find("Skip") or card.find("Draw") or card.find("Reverse"):
                points += 20
            else:
                points += int(card[card.find("_") + 1:])
        return points

    def endTurn(self, special):
        global reverse
        try: CheckSide.place_forget()
        except: pass
        # set up effects
        increment = 1
        drawAmt = False
        if special == "Skip": increment = 2
        elif special == "Reverse":
            if len(players) > 2:
                reverse = not reverse
            else: # function like a skip turn
                increment = 2
        elif special == "Draw_2": drawAmt = 2
        elif special == "Draw_4": drawAmt = 4
        # end turn
        self.turn = False
        self.drawn = False
        self.ScoreLabel["fg"] = "Black"
        # get position in list of current player
        for i, v in enumerate(players):
            if v == self:
                n = i
                break
        # find next player's turn
        if reverse: n -= increment
        else: n += increment
        if n > len(players)-1: n -= len(players)
        elif n < 0: n += len(players)

        plr = players[n]
        if drawAmt > 0:
            plr.draw(drawAmt)
            plr.endTurn(None)
        else:
            plr.turn = True
            plr.ScoreLabel["fg"] = "Red"
                      
    def drawFromDeck(self):
        if self.turn and not self.drawn:
            self.drawn = True
            self.draw(1)
            card = self.lastDrawn
            # Not wild, not same colour and not same type (number, action)
            if not isValidCard(card):
                self.endTurn(None)
            else:
                CheckSide.place(relx=0.35, rely=0.5, anchor="w")
                checkImage["image"] = images[card]

    def botPlay(self):
        # Self-Note: MAKE THIS BETTER
        usableCards = []
        for card in self.hand:
            # not wild, not right colour, not right type
            if isValidCard(card):
                usableCards.append(card)
        if len(usableCards) == 0:
            self.draw(1)
            if isValidCard(self.hand[-1]):
                self.useCard(None, card)
            else:
                self.endTurn(None)
        else:
            canPlayWild = True
            appearances = {}
            for card in usableCards:
                # same Colour owned
                if lastPlayed[:lastPlayed.find("_")] != card[:card.find("_")]:
                    canPlayWild = False
                try:
                    appearances[card[:card.find("_")]] += 1
                except:
                    appearances[card[:card.find("_")]] = 1
            mostAppeared = [None, 0]
            for i in appearances:
                if appearances[i] > mostAppeared[1]:
                    mostAppeared = [i, appearances[i]]
            card = ""
            for i in usableCards:
                if mostAppeared[0] != i[:i.find("_")]:
                    card = i
            if card == "": card = usableCards[random(0, len(usableCards)-1)]
            self.useCard(None, card)
            
def generateDeck(dictionary):
    unshuffledDeck = []
    for i, value in enumerate(cardsInDeck):
        mainDictionary = cardsInDeck[value]
        for j, v in enumerate(mainDictionary):
            if i == 0:
                for n in range(mainDictionary[v]):
                    unshuffledDeck.append(v)
            else:
                for k, v2 in enumerate(mainDictionary[v]):
                    unshuffledDeck.append(f"{v}_{v2}")
    shuffle(unshuffledDeck)  
    return unshuffledDeck

def gameOver(winner):
    for plr in players:
        winner.score += plr.handWorth()
        plr.restart(False)
    players[0].turn = True
    players[0].ScoreLabel["fg"] = "Red"
    winner.ScoreLabel["text"] = f"{winner.name}: {winner.score}"

def changeColour(col):
    global Colour, lastPlayed
    # Use Colour Picker UI for wild cards
    ColourPicker.place(relx=0.3, rely=0.5, anchor="w")
    root.update()
    Colour = col
    if Colour: 
        ColourPicker.place_forget()
        ColourChosen.place(relx=0.3, rely=0.5, anchor="w")
        ColourChosen["bg"] = col
        lastPlayed = f"{Colour}_Wild"

def addColour(Colour, x, y, anch):
    # Set up Colour picker UI for wild cards
    ButtonFrame = Frame(ColourPicker, width=100, height=100, bg=Colour)
    ButtonFrame.place(relx=x, rely=y, anchor=anch)
    ButtonFrame.bind("<Button-1>", lambda e: changeColour(Colour))

def isValidCard(card):
    # Check if not wild, not same colour & not same type
    if card.find("Wild") == -1 and lastPlayed[:lastPlayed.find("_")] != card[:card.find("_")] and lastPlayed[lastPlayed.find("_")+1:] != card[card.find("_")+1:]:
        return False
    else:
        return True

def unoTrue():
    global uno
    uno = True

def makePlayers(n):
    global player
    try: n = int(n.get())
    except: n = 2
    # if amount < 2 or > 4, you get forced to have 2 and 4, respectively.
    print(n)
    if n <= 2:
        player = player = Player("Player", "s", 0.5, 1, False, False, .35)
        computer1 = Player("Computer2", "n", 0.5, 0, False, True, .7)
    elif n >= 3: 
        player = player = Player("Player", "s", 0.5, 1, False, False, .2)
        computer1 = Player("Computer2", "e", 1, 0.5, False, True, .4)
        computer2 = Player("Computer3", "n", 0.5, 0, False, True, .6)
        if n >= 4:
            computer3 = Player("Computer4", "w", 0, 0.5, False, True, .8)
    player.turn = True
    player.ScoreLabel["fg"] = "Red"

# Background
canvas.create_image(0, 0, anchor="nw", image=images[backgroundImage])
# Find how many players wanted
playerCountLabel = Label(canvas, height=3, font=(fontType, 20), bg=pseudoBackground, text="Input how many players you want: (2-4)")
playerCountLabel.place(relx=0.5, rely=0.4, anchor="s")
playerCountInput = Text(canvas, font=(fontType, 50), width=10, height=1, wrap=None)
playerCountInput.place(relx=0.5, rely=0.5, anchor=CENTER)
playerCountButton = Button(canvas, text="START", font=fontInfo, command= lambda: playerCount.set(playerCountInput.get("1.0", "end-1c")))
playerCountButton.place(relx=0.5, rely=0.6, anchor="n")
root.update()
playerCountButton.wait_variable(playerCount)
# Got amount, destroy stuff
playerCountButton.destroy()
playerCountInput.destroy()
playerCountLabel.destroy()

# Show deck image, uno button, bind drawing from deck & UNO on last card
drawDeck.place(relx=0.58, rely=0.5, anchor=CENTER)
drawDeck.bind("<Button-1>", lambda e: player.drawFromDeck())
UnoButton = Label(canvas, width=82, height=58, image=images["UNO_Button"], bg=pseudoBackground)
UnoButton.place(relx=0.58,rely=0.63, anchor="n")
UnoButton.bind("<Button-1>", lambda e: unoTrue())
root.update()

# generate deck, show image
deck = generateDeck(cardsInDeck)
for i in deck:
    name = f"{folder}/{i}.png"
    try:
        images[i]
    except:
        images[i] = PhotoImage(file=name)

# Create colour pickers for wild cards
ColourPicker = Frame(canvas, width=200, height=200)
ColourChosen = Frame(canvas, width=200, height=200)
addColour("Red", 0, 0, "nw")
addColour("Blue", 0,1,  "sw")
addColour("Green", 1, 0, "ne")
addColour("Yellow", 1, 1, "se")

# Create UI for choosing whether to use the card drawn or not
checkImage = Label(CheckSide, image = images[lastPlayed])
checkImage.place(relx=0.5,rely=0,anchor="n")
useButton = Button(CheckSide, text="Use Card", command=lambda: player.useCard(None, player.lastDrawn))
endButton = Button(CheckSide, text="End Turn", command=lambda: player.endTurn(None))
useButton.place(relx=0.5,rely=0.6, anchor=CENTER)
endButton.place(relx=0.5,rely=0.8, anchor=CENTER)

makePlayers(playerCount)

# Put top of card into discard pile, act accordingly to result
lastPlayed = deck[0]
if lastPlayed.find("Skip") != -1 or lastPlayed.find("Reverse") != -1:
    player.endTurn(lastPlayed[lastPlayed.find("_")+1:])
elif lastPlayed == "Wild_Draw":
    while lastPlayed == "Wild_Draw":
        shuffle(deck)
        lastPlayed = deck[0]
elif lastPlayed.find("Wild") != -1:
    changeColour(None)
elif lastPlayed.find("Draw") != -1: # not wild, normal draw
    player.draw(2)
    player.endTurn(None)
    
deck.pop(0)
usedPileCard = Label(canvas, image=images[lastPlayed], bg=pseudoBackground)
usedPileCard.place(relx=0.5, rely=0.5, anchor=CENTER)
oldDiscardPile.append(CheckSide = Frame(canvas, width=100,height=200,bg=pseudoBackground)

# Set up Uno symbol
UnoSign = Label(canvas, width=410, height=288, image=images["UNO"], bg=pseudoBackground)
root.update()

# For the computer's moves
while True:
    sleep(0.01)
    root.update()
    if not player.turn:
        sleep(computerDelay)
        for i in players:
            if i.turn:
                i.botPlay()
                break
