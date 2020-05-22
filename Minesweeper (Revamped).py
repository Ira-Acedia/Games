from tkinter import *
from random import randint
from threading import Thread
from time import sleep

root = Tk()
col = "lightgoldenrodyellow"
root.geometry("800x650")
root.title("Minesweeper 2.0")
root.resizable(False,False)
root.configure(bg=col)

bombs = 40
tileSize = 40
headerY = (650-(14*tileSize))//2.5
headerX = (800-(18*tileSize))//1.5
resultCol = "azure"
folder = "Minesweeper_Assets"
images = {
    "tile": PhotoImage(file=f"{folder}/tile.png"),
    "bomb": PhotoImage(file=f"{folder}/bomb.png"),
    "flag": PhotoImage(file=f"{folder}/flagPlaced.png"),
    "wrongFlag": PhotoImage(file=f"{folder}/badFlag.png"),
    "explosion": PhotoImage(file=f"{folder}/explosion.png"),
    "flagIcon": PhotoImage(file=f"{folder}/flag.png"),
    "trophy": PhotoImage(file=f"{folder}/trophy.png"),
    "timer": PhotoImage(file=f"{folder}/timer.png"),
    "restart": PhotoImage(file=f"{folder}/restart.png"),
    "resultFrame": PhotoImage(file=f"{folder}/resultFrame.png"),
    "values": [
        PhotoImage(file=f"{folder}/zero.png"),
        PhotoImage(file=f"{folder}/one.png"),
        PhotoImage(file=f"{folder}/two.png"),
        PhotoImage(file=f"{folder}/three.png"),
        PhotoImage(file=f"{folder}/four.png"),
        PhotoImage(file=f"{folder}/five.png"),
        PhotoImage(file=f"{folder}/six.png"),
        PhotoImage(file=f"{folder}/seven.png"),
        PhotoImage(file=f"{folder}/eight.png")
        ]
    }

tiles = {}
started = False
playing = True
flags = 0
bestTime = ""

canvas = Canvas(root,width=tileSize*18,height=tileSize*14,
                bg=col, highlightthickness=0)
canvas.place(relx=0.5, rely=0.5, anchor=CENTER)

class Tile():
    def reset(self):
        self.flagged = False
        self.isBomb = False
        self.shown = False
        self.unbombable = False
        self.value = 0
        canvas.itemconfig(self.main, image= images["tile"])
    
    def __init__(self, posX, posY):
        #self.main = Label(canvas, image=images["tile"])
        #self.main.place(x=posX*tileSize, y=posY*tileSize)
        self.main = canvas.create_image(posX*tileSize, posY*tileSize,
                            image=images["tile"],
                            anchor="nw")
        canvas.tag_bind(self.main, "<1>", self.clicked)
        canvas.tag_bind(self.main, "<3>", self.flagged)
        self.reset()
        self.surrounding = []
        for x in range(-1,2):
            netX = posX + x
            for y in range(-1,2):
                # Not current tile (middle). Falls within x & y constraints
                netY = posY + y
                if not (x==0 and y==0) and netX >= 0 and netX <= 17 and netY >= 0 and netY <= 13:
                    self.surrounding.append(f"{netX}.{netY}")
    
    def clicked(self, event):
        global started
        if self.flagged or self.shown or not playing: # Flagged or already visible or game over
            return
        elif self.isBomb: # Mine!
            gameFailed(self.main)
            return

        # Update appearance
        self.shown = True
        canvas.itemconfig(self.main, image= images["values"][self.value])
        for index in self.surrounding:
            tiles[index].unbombable = True
            
        if not started: # First click so generate map
            genBombs(bombs)
            started = True
            clock.thread.start()
        if self.value == 0: # no surrounding bombs, so auto click surrounding tiles.
            for index in self.surrounding:
                tiles[index].clicked(0)

        # Check if won
        for i, tile in tiles.items():
            if not tile.shown and not tile.isBomb: # Stop if 1 non-bomb isn't shown
                return
        # Only bombs hidden
        gameWon()

    def flagged(self, event):
        global flags
        if not playing:
            return
        # Unflagging
        if self.flagged:
            canvas.itemconfig(self.main, image= images["tile"])
            flags += 1
            self.flagged = not self.flagged
        elif flags > 0 and not self.shown: # Any flags left? Can it be flagged?
            canvas.itemconfig(self.main, image= images["flag"])
            flags -= 1
            self.flagged = not self.flagged
        flagsLabel["text"] = f"{flags}"

class Clock():
    def reset(self):
        self.days = 0
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.format = "{self.seconds}"
        self.level = 1
        self.visuals = ""
        self.playing = True
        self.thread = Thread(target=self.start, args=(1,))
        
    def __init__(self):
        self.reset()

    def add(self, secs):
        global timerLabel
        self.seconds += secs
        if self.seconds >= 60:
            # Change secs to mins
            self.minutes += self.seconds//60
            self.seconds %= 60
            if self.level < 2: # First minute, change format
                self.level = 2
                self.format = "{self.minutes}:{self.seconds}"
            if self.minutes >= 60:
                # Change mins to hours
                self.hours += self.minutes//60
                self.minutes %= 60
                if self.level < 3: # First hour, change format
                    self.level = 3
                    self.format = "{self.hours}:{self.minutes}:{self.seconds}"
                if self.hours >= 24:
                    # Change hours to days
                    self.days += self.hours//24
                    self.hours %= 24
                    if self.level < 4: # First day, change format
                        self.level = 4
                        self.format = "{self.days}:{self.hours}:{self.minutes}:{self.seconds}"
        self.visuals = fstr(self)
        timerLabel["text"] = self.visuals
        
    def convertToSeconds(self, time):
        level = time.count(":")
        seconds = 0
        if level >= 3: # Convert days to hours
            hours = int(time[:time.find(":")])*24
            time = time[time.find(":")+1:]
        if level >= 2: # Convert hours to minutes
            minutes = (hours + int(time[:time.find(":")]))*60
            time = time[time.find(":")+1:]
        if level >= 1: # Convert minutes to seconds
            seconds = (minutes + int(time[:time.find(":")]))*60
            time = time[time.find(":")+1:]
        # Register seconds
        seconds += int(time)
        return seconds

    def start(self, interval):
        while playing:
            sleep(interval)
            self.add(interval)
        
def genBombs(amount):
    global flags
    # Adds bombs
    flags = amount
    clock.Playing = True
    while amount != 0:
        x = randint(0, 17)
        y = randint(0, 13)
        if not tiles[f"{x}.{y}"].isBomb and not tiles[f"{x}.{y}"].shown and not tiles[f"{x}.{y}"].unbombable:
            # Not already a bomb and not visible, so plant bomb and decrease
            tiles[f"{x}.{y}"].isBomb = True
            amount -= 1
        # If it is a bomb, no changes made
        
    # Update tile values
    for i, tile in tiles.items():
        # Skip bombs
        if tile.isBomb:
            continue
        # Get all surroundings bombs
        for index in tile.surrounding:
            if tiles[index].isBomb:
                tile.value += 1

def displayResults(text):
    resultFrame.place(relx=0.5,rely=0.5, anchor=CENTER)
    resultTimeLabel["text"] = clock.visuals
    recordTimeLabel["text"] = bestTime
    bestTimeLabel["text"] = bestTime
    timerLabel["text"] = "0"
    feedback["text"] = text

def restartGame(event):
    global started, playing
    resultFrame.place_forget() # Hide results
    flags = 0
    clock.reset()
    started = False
    playing = True
    for i, tile in tiles.items():
        tile.reset()
        
def gameFailed(triggerBomb):
    global playing
    playing = False
    clock.playing = False
    # Show all unflagged bombs
    for i, tile in tiles.items():
        if tile.isBomb and not tile.flagged:
            canvas.itemconfig(tile.main, image= images["bomb"])
        elif tile.flagged: # not bomb, but flagged. show error
            canvas.itemconfig(tile.main, image= images["wrongFlag"])
    # Show clicked bomb
    canvas.itemconfig(triggerBomb, image= images["explosion"])
    displayResults("You lost! :(")

def gameWon():
    global playing, bestTime
    playing = False
    clock.playing = False
    # Update the best time, if necessary
    if bestTime == "" or clock.convertToSeconds(bestTime) > clock.convertToSeconds(clock.visuals):
        bestTime = clock.visuals

    displayResults("You won!")

def fstr(self): # allows usage of f-strings without string literal
    return str(eval(f"f'{self.format}'"))

def createPairedCounter(parent, picture, baseText, textCol, yPad, bg): # Pair = image + label. for timer etc & result label
    img = Label(parent, image=images[picture], bg=bg)
    label = Label(parent, text=baseText, font=("Arial", 20), bg=bg, fg=textCol)
    img.place(x=0, y=0, anchor="nw")
    label.place(x=35, y=yPad, anchor="nw")
    return label

# Create tiles
for x in range(18):
    for y in range(14):
        tiles[f"{x}.{y}"] = Tile(x, y)

clock = Clock()
# Setup visual displays
timerFrame = Frame(root, width=(800//5),height=30, bg=col)
bestTimeFrame = Frame(root, width=(800//5), height=36, bg=col)
flagsFrame = Frame(root, width=70, height=30, bg=col)

# Flag counter display
flagsFrame.place(x=headerX, y=headerY, anchor="sw")
flagsLabel = createPairedCounter(flagsFrame, "flagIcon", f"{bombs}", "red", -3, col)

# Current time display
timerFrame.place(x=headerX+(800//5)+5, y=headerY, anchor="sw")
timerLabel = createPairedCounter(timerFrame, "timer", "0", "grey", -3, col)

# Record time display
bestTimeFrame.place(x=headerX+2*(800//5)+10, y=headerY+3, anchor="sw")
bestTimeLabel = createPairedCounter(bestTimeFrame, "trophy", "0", "grey", 0, col)

# Setup result frame
resultFrame = Label(root, width=400, height=275, bg=resultCol, image=images["resultFrame"])

# Timers
resultTimeFrame = Frame(resultFrame, width=200, height=30, bg=resultCol)
recordTimeFrame = Frame(resultFrame, width=200, height=36, bg=resultCol)
resultTimeLabel = createPairedCounter(resultTimeFrame, "timer", "0", "grey", -3, resultCol)
recordTimeLabel = createPairedCounter(recordTimeFrame, "trophy", "0", "grey", 0, resultCol)
resultTimeFrame.place(relx=0.15, y=15, anchor="nw")
recordTimeFrame.place(relx=0.15, y=55, anchor="nw")

# Feedback text
feedback = Label(resultFrame, font=("Arial", 30), bg=resultCol, text="Test!")
feedback.place(relx=0.5, y=100, anchor="n")

# Restart Button
restartButton = Label(resultFrame, image=images["restart"], bg=resultCol)
restartButton.place(relx=0.5, y=150, anchor="n")
restartButton.bind("<1>", restartGame)

root.mainloop()
