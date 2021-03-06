from tkinter import *
from random import choices
from operator import itemgetter
from functools import partial

rootCol = "lightgoldenrodyellow"
root = Tk()
root.geometry("500x400")
root.title("Mastermind Game")
root.resizable(False,False)
root.configure(bg=rootCol)

# Constants
possibleColours = ["Blue", "White", "Orange", "Green", "Red", "Yellow"]
fontSize = 20
fontType = "Arial"
fontInfo = (fontType, fontSize)
bgHex = "#ADBEC9" # Background hex colour
folder = "Mastermind_Assets"
leaderboardFile = f"{folder}/leaderboard.txt"
rows = 12
rulesString = f'''Mastermind Rules
 - Computer generates a random 4 colour code (colours can repeat).
 - The player chooses four code pegs per attempt to try and crack the code.
 - If a colour is correct, but in the wrong place, a white peg will be placed into the small holes.
 - If a colour is correct, and in the right place, a black peg will be placed into the small holes.
 - If duplicate colours are guessed, the max amount of pegs placed (for that colour) correspond to the amount of times that colour appears in the code.
 - If the player is unable to do this within {rows} tries, they lose.
 - If they're able to crack the code, they win!
'''

loseString = '''
Unfortunately, %s, you lost!
The correct solution was:
'''

winString = '''
Congratulations, %s, you won!
It took you %d %s!
''' 

images = {
    "PegHole": PhotoImage(file=f"{folder}/pegHole.png"),
    "MiniHole": PhotoImage(file=f"{folder}/feedbackPegHole.png"),
    "MiniHole_Black": PhotoImage(file=f"{folder}/feedbackPegHole_B.png"),
    "MiniHole_White": PhotoImage(file=f"{folder}/feedbackPegHole_W.png"),
    "Blue_Peg": PhotoImage(file=f"{folder}/BluePeg.png"),
    "White_Peg": PhotoImage(file=f"{folder}/WhitePeg.png"),
    "Orange_Peg": PhotoImage(file=f"{folder}/OrangePeg.png"),
    "Green_Peg": PhotoImage(file=f"{folder}/GreenPeg.png"),
    "Red_Peg": PhotoImage(file=f"{folder}/RedPeg.png"),
    "Yellow_Peg": PhotoImage(file=f"{folder}/YellowPeg.png"),
    "PegHole_Blue": PhotoImage(file=f"{folder}/pegHole_Blue.png"),
    "PegHole_Red": PhotoImage(file=f"{folder}/pegHole_Red.png"),
    "PegHole_Orange": PhotoImage(file=f"{folder}/pegHole_Orange.png"),
    "PegHole_White": PhotoImage(file=f"{folder}/pegHole_White.png"),
    "PegHole_Yellow": PhotoImage(file=f"{folder}/pegHole_Yellow.png"),
    "PegHole_Green": PhotoImage(file=f"{folder}/pegHole_Green.png")    
    }


# These change during the code (variables)
currRow = 0
playerName = StringVar()
rowList = []
pegList = []
solutionList = []
correctCode = choices(possibleColours, k=4) # generate code

class PegHole(): 
    def __init__(self, position, colour, parent):
        self.colour = colour
        if self.colour != None:
            self.image = images[f"PegHole_{colour}"]
            backGround = rootCol
        else:
            self.image = images["PegHole"]
            backGround = bgHex
        self.label = Label(parent, image=self.image, bg=backGround)
        if self.colour == None:
            self.label.bind("<1>", lambda e: self.removeColour())
        self.label.place(relx=position/5)
        
    def changeColour(self, colour):
        self.colour = colour
        self.image = images[f"PegHole_{colour}"]
        self.label["image"] = self.image

    def removeColour(self):
        self.image = images["PegHole"]
        self.label["image"] = self.image
        self.colour = None
        checkButton.place_forget()

def placePNEntries(): # place PlayerName entries
    playerNameLabel.place(relx=0.5, rely=0.4, anchor="s")
    playerNameInput.place(relx=0.5, rely=0.5, anchor=CENTER)
    startButton.place(relx=0.5, rely=0.65, anchor="n")
    rulesButton.place(relx=0.1, rely=0.8)
    # hide rule-related widgets
    backButton.place_forget()
    rulesLabel.place_forget()
    
    
def hidePNEntries(showRules): # hides playerName widgets, can show rule widgets
    # hide PlayerName Entries
    playerNameLabel.place_forget()
    playerNameInput.place_forget()
    startButton.place_forget()
    rulesButton.place_forget()
    if showRules:
        # show rule-related widgets
        backButton.place(relx=0.1, rely=0.8)
        rulesLabel.place(relx=0.5, rely=0.4, anchor = CENTER)

def pegMoving(pegImage, event):
    duplicateHolder["image"] = pegImage
    x, y = root.winfo_pointerxy()
    x -= root.winfo_rootx()
    y -= root.winfo_rooty()
    duplicateHolder.place(x=x,y=y, anchor=CENTER)
    
def pegDropped(colour, event):
    # find the widget under the cursor
    duplicateHolder.place_forget()
    x,y = event.widget.winfo_pointerxy()
    target = event.widget.winfo_containing(x,y)
    try:
        # fixed row input
        x, y = int(target.winfo_x()/60), currRow
    except: pass

    # not correct widget, so change last one in row
    if target.winfo_width() != 64:
        y = currRow
        x = -2
        # get next empty spot
        for i, obj in enumerate(rowList[y]):
            if type(obj) == list:
                break
            elif not obj.colour:
                x = i
                break

    # update row colours
    rowList[y][x].changeColour(colour)
    currCode = []
    for obj in rowList[y]:
        if type(obj) == list or not obj.colour:
            break
        else:
            currCode.append(obj.colour)

    # check whether they're able to validate their code
    if len(currCode) == 4:
        checkButton.place(relx=0.02, rely=0.83)
        checkButton["command"] = lambda: validateCode(currCode)
    else:
        checkButton.place_forget()
        
def validateCode(currCode):
    global currRow
    checkButton.place_forget()
    for obj in rowList[currRow]:
        if type(obj) != list:
            obj.label.unbind("<1>")
    currRow += 1
    if currCode == correctCode:
        # won
        gameOver(True)
    elif currRow >= rows:
        # lost
        gameOver(False)
    else:
        # still playing
        ''' feedback format
        "R" = Correct colour, wrong place (White)
        "P" = Correct Colour, Right Place (Black)
        otherwise Wrong colour, wrong place (no image change)
        '''
        feedback = []
        remCorrectCode = [] # remaining correct code
        appeared = {}
        for index, colour in enumerate(currCode):
            # Check whether both correct
            if colour == correctCode[index]:
                feedback.append("P")
            else: # else, collect incorrectly placed colours
                try:
                    appeared[colour] += 1
                except:
                    appeared[colour] = 1
                remCorrectCode.append(correctCode[index])
                
        # check incorrectly placed colours for correct colours
        for colour in appeared:
            if appeared[colour] > remCorrectCode.count(colour): # too many appearances
                appeared[colour] = remCorrectCode.count(colour)
            # if >0 appearances of that colour, then append it to feedback
            for i in range(appeared[colour]):
                feedback.append("R")

        # visually show feedback
        container = rowList[currRow-1][-1]
        # variable used in favour of enumerate() index, to avoid having gaps in the feedback
        for n, v in enumerate(feedback):
            if v == "P":
                # change Black
                container[n]["image"] = images["MiniHole_Black"]
            else:
                container[n]["image"] = images["MiniHole_White"]     
        
def resetRow():
    for obj in rowList[currRow]:
        if type(obj) != list:
            obj.removeColour()

def newGame():
    global correctCode, currRow
    # Re-adjust window
    root.geometry("500x730")
    board.place(relx = .98, rely = 0.5, anchor="e")
    pegFrame.place(relx=0.02, rely=0.02)
    resetButton.place(relx=0.02, rely=0.73)
    newGameButton.place_forget()
    solutionFrame.place_forget()
    gameOverLabel.place_forget()
    leaderboardButton.place_forget()
    # Reset variables
    correctCode = choices(possibleColours, k=4)
    currRow = 0
    # Update solution for game over
    for i, obj in enumerate(solutionList):
        obj.changeColour(correctCode[j])

    # Reset board
    for row in rowList:
        for obj in row:
            if type(obj) != list:
                obj.removeColour()
            else: # list
                for hole in obj:
                    hole["image"] = images["MiniHole"]

def hideLeaderboard():
    hideLeaderboardButton.place_forget()
    leaderboardLabel.place_forget()
    newGameButton.place(relx=0.1, rely=0.8)
    gameOverLabel.place(relx=0.5, rely=0.4, anchor = CENTER)
    leaderboardButton.place(relx=0.9, rely=0.9, anchor="se")
    solutionFrame.place(relx=0.5, rely=0.7, anchor=CENTER)
    
def showLeaderboard(text):
    leaderboardButton.place_forget()
    newGameButton.place_forget()
    gameOverLabel.place_forget()
    solutionFrame.place_forget()
    hideLeaderboardButton.place(relx=0.1, rely=0.8)
    leaderboardLabel.place(relx=0.5, rely=0.4, anchor = CENTER)
    leaderboardLabel["text"] = text
    
def gameOver(won):
    data = {}
    if won: # they won!
        if currRow == 1:
            gameOverLabel["text"] = winString % (playerName, 1, "try")
        else:
            gameOverLabel["text"] = winString % (playerName, currRow, "tries")
        with open(leaderboardFile, "a") as aFile:
            aFile.write(f"{playerName}; {currRow}\n")
    else: # they lost! :(
        gameOverLabel["text"] = loseString % playerName
        
    board.place_forget()
    pegFrame.place_forget()
    resetButton.place_forget()
    root.geometry("500x400")
    newGameButton.place(relx=0.1, rely=0.8)
    gameOverLabel.place(relx=0.5, rely=0.4, anchor = CENTER)
    leaderboardButton.place(relx=0.9, rely=0.9, anchor="se")
    solutionFrame.place(relx=0.5, rely=0.7, anchor=CENTER)
    '''
        Question asks for the 3 players with the least tries
        Not the 3 lowest tries and who got them
        So only record the least tries for each player
    '''
    with open(leaderboardFile)as aFile:
        for line in aFile:
            fields = line.rstrip("\n").split("; ")
            name = fields[0]
            try:
                if data[name] > fields[-1]: # old value took more tries
                    data[name] = fields[-1]
            except: # no prior data
                data[name] = fields[-1]

    # turn dictionary into list of tuples
    data = list(data.items())
    leaderboardString = "Leaderboard:\n"
    # get 3 lowest, or as many as possible (if <3)
    # if 3>data then use data, else use 3
    for i in range((3>len(data) and len(data)) or 3):
        # get tuple with lowest tries
        tup = min(data, key=itemgetter(1))
        tries = "tries"
        if tup[0] == 1:
            tries = "try"            
        leaderboardString += f"{tup[0]}: {tup[1]} {tries}\n"
        data.remove(tup)
    # when click show leaderboard, show leaderboard (obviously)
    leaderboardButton["command"] = lambda: showLeaderboard(leaderboardString)
    
# Initalise entry for entering playerName
playerNameLabel = Label(root, height=3, font=fontInfo, bg=rootCol, text="Enter your name: ")
playerNameInput = Text(root, font=(fontType, 50), width=10, height=1, wrap=None)
startButton = Button(root, text="START", font=fontInfo, command = lambda: playerName.set(playerNameInput.get("1.0", "end-1c")))
# Initialise rule-related widgets
rulesButton = Button(root, text="Rules", font=fontInfo, command = lambda: hidePNEntries(True))
backButton = Button(root, text="Back", font=fontInfo, command = placePNEntries)
rulesLabel = Label(root, font=(fontType, 13), bg=rootCol, text=rulesString, wraplength=400, justify=LEFT)
# Show playerName-related widgets
placePNEntries()
# Wait for button press
startButton.wait_variable(playerName)
# Hide all previously created widgets.
hidePNEntries(False)

# Validate playerName input
if playerName.get().isalpha() and len(playerName.get()) >= 3:
    playerName = playerName.get()
else:
    playerName = "Player"

# Create board
root.geometry("500x730")
board = Canvas(root, width= 300, height=720, bg=bgHex)
board.place(relx = .98, rely = 0.5, anchor="e")
            
'''
rowList layout:

rowList = [
    row [pegHole, pegHole, pegHole, pegHole, feedBackPegs [pegHole, pegHole, pegHole, pegHole]],
    row [pegHole, pegHole, pegHole, pegHole, feedBackPegs [pegHole, pegHole, pegHole, pegHole]],
    row ...

    hence:
        rowList[-1] = last row
        rowList[0-12] = rows
        
        rowList[-1][0-4] = peg holes
        rowList[-1][-1] = feedback peg container
        rowList[-1][-1][0-4] = feedback peg holes

    in the following code, "-1"s can usually be replaced by the for loop variable names (e.g. i, j etc)
    However, -1 is used to make it easier to understand.
]
'''

# Create invisible solution frame (for game over)
solutionFrame = Frame(root ,width=300, height=720/rows, bg=rootCol)
for j in range(4):
    solutionList.append(PegHole(j, correctCode[j], solutionFrame))
    
# Create canvas board
for i in range(rows):
    # Create row container
    frame = Frame(board, width = 300, height=720/rows, bg=bgHex)
    frame.place(relx = 0.5, rely=i/rows, anchor="n")
    rowList.append([])
    # create main row objects
    for j in range(4):
        rowList[-1].append(PegHole(j, None, frame))
    # create feedback pin container
    pegContainer = Frame(frame, width= 300/5, height=780/rows, bg=bgHex)
    pegContainer.place(relx=4/5)
    rowList[-1].append([])
    # create feedback pin holes
    for j in range(2):
        for k in range(2):
            rowList[-1][-1].append(Label(pegContainer, bg=bgHex, image=images["MiniHole"]))
            rowList[-1][-1][-1].place(relx=k/2,rely=j/2)
        
# Create pegs
pegFrame = Frame(root, width=69, height=(len(possibleColours)+1)*74, bg=rootCol) # pegs = 68x74 pixels
pegFrame.place(relx=0.02, rely=0.02)

for i, v in enumerate(possibleColours):
    pegImage = images[f"{v}_Peg"]
    pegList.append(Label(pegFrame, image=pegImage, bg=rootCol))
    pegList[-1].place(rely=i/6)
    pegList[-1].bind("<ButtonRelease-1>", partial(pegDropped, v))
    pegList[-1].bind("<B1-Motion>", partial(pegMoving, pegImage))

#  Make buttons
checkButton = Button(root, text="CHECK", font=fontInfo)
resetButton = Button(root, text="RESET", font=fontInfo, command=resetRow)
resetButton.place(relx=0.02, rely=0.73)
newGameButton = Button(root, text="NEW GAME", font=fontInfo, command=newGame)
leaderboardButton = Button(root, text="SHOW LEADERBOARD", font=(fontType,12))
hideLeaderboardButton = Button(root, text="BACK", font=fontInfo, command=hideLeaderboard)
# Make labels
gameOverLabel = Label(root, font=fontInfo, bg=rootCol, text=rulesString, wraplength=400, justify=LEFT)
leaderboardLabel = Label(root, font=fontInfo, bg=rootCol, text=rulesString, wraplength=400, justify=LEFT)
duplicateHolder = Label(root, bg=rootCol)
