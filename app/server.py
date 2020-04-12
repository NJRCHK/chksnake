import json
import os
import random
import bottle
from bottle import HTTPResponse


@bottle.route("/")
def index():
	return "Your Battlesnake is alive!"

@bottle.post("/ping")
def ping():
	"""
	Used by the Battlesnake Engine to make sure your snake is still working.
	"""
	return HTTPResponse(status=200)

@bottle.post("/start")
def start():
	"""
	Called every time a new Battlesnake game starts and your snake is in it.
	Your response will control how your snake is displayed on the board.
	"""
	data = bottle.request.json
	("START:", json.dumps(data))

	response = {"color": "#4F1851", "headType": "evil", "tailType": "hook"}
	return HTTPResponse(
		status=200,
		headers={"Content-Type": "application/json"},
		body=json.dumps(response),
	)

@bottle.post("/move")
def move():
	"""
	Called when the Battlesnake Engine needs to know your next move.
	The data parameter will contain information about the board.
	Your response must include your move of up, down, left, or right.
	"""

	data = bottle.request.json
	# THE BEST MOVE IS CALUCLATED USING A FLOODFILL. HIGHEST AREA WIN. ME SPEEL GOOD
	move = ""
	print(str(data))


	upC = floodFill(getNextPosition("up", data), data, arrayify("up", data, not largestSnake(data)))
	downC = floodFill(getNextPosition("down", data), data, arrayify("down", data, not largestSnake(data)))
	rightC = floodFill(getNextPosition("right", data), data, arrayify("right", data, not largestSnake(data)))
	leftC = floodFill(getNextPosition("left", data),  data, arrayify("left", data, not largestSnake(data)))
	moveC = [upC, downC, rightC, leftC]
	#if moveC cannot find a viable move with ghostheads, it disables them so the snake doesn't kill itself

	move = goto(moveC, findFood(data), data)

	if isStuck(moveC, data):
		if upC == max(moveC):
			move = "up"
		elif downC == max(moveC):
			move = "down"
		elif leftC == max(moveC):
			move = "left"
		elif rightC == max(moveC):
			move = "right"

	if max(moveC) == 0:
		upC = floodFill(getNextPosition("up", data), data, arrayify("up", data, False))
		downC = floodFill(getNextPosition("down", data), data, arrayify("down", data, False))
		rightC = floodFill(getNextPosition("right", data), data, arrayify("right", data, False))
		leftC = floodFill(getNextPosition("left", data),  data, arrayify("left", data, False))
		moveC = [upC, downC, rightC, leftC]


	if move == "":
		goodMoves = []
		if upC == max(moveC):
			goodMoves.append("up")
		if downC == max(moveC):
			goodMoves.append("down")
		if leftC == max(moveC):
			goodMoves.append("left")
		if rightC == max(moveC):
			goodMoves.append("right")
		move = random.choice(goodMoves)

	response = {"move": move, "shout": "yeet"}
	return HTTPResponse(
		status=200,
		headers={"Content-Type": "application/json"},
		body=json.dumps(response),
	)


@bottle.post("/end")
def end():
	"""
	Called every time a game with your snake in it ends.
	"""
	data = bottle.request.json
	return HTTPResponse(status=200)

def isStuck(moveC, data):
	body_length = len(data["you"]["body"])
	if max(moveC) < body_length:
		return True
	return False


def getNextPosition(move, data):
	"""
	returns next position depending on which inputted
	"""
	nextPos = {"x": data["you"]["body"][0]['x'],
				"y": data["you"]["body"][0]['y']}

	if move == 'up':
		nextPos["y"] = nextPos["y"] - 1
	elif move == 'down':
		nextPos["y"] = nextPos["y"] + 1
	elif move == 'right':
		nextPos["x"] = nextPos["x"] + 1
	elif move == 'left'	:
		nextPos["x"] = nextPos["x"] - 1
	return nextPos

def floodFill(pos, data, dataArray):
	"""
	checks how much room there is if snake does a move
	used so snake doesn't run into a corner
	returns free space
	"""
	count = 0
	try:
		if dataArray[pos["y"]][pos["x"]] == 1 or pos["x"] not in range (0, data["board"]["width"]) or pos["y"] not in range(0, data["board"]["height"]):
			return count
		else:
			dataArray[pos["y"]][pos["x"]] = 1
	except IndexError:
		return count

	count += 1
	count += floodFill({"x": pos["x"], "y": pos["y"]-1}, data, dataArray)
	count += floodFill({"x": pos["x"], "y": pos["y"]+1}, data, dataArray)
	count += floodFill({"x": pos["x"]-1, "y": pos["y"]}, data, dataArray)
	count += floodFill({"x": pos["x"]+1, "y": pos["y"]}, data, dataArray)

	return count


def arrayify(nextMove, data, ghost_head_enabled):
	"""
	returns state of board as a 2d array. used for floodFill
	"""
	n = data["board"]["height"]
	m = data["board"]["width"]
	a = [[0] * m for i in range(n)]

	snakes = data["board"]["snakes"]
	snake_bodies = [body for snake in snakes for body in snake['body'][:-1]]

	for x in snake_bodies:
		a[x['y']][x['x']] = 1
		for snake in snakes:
			if (snake["id"] != data["you"]["id"]) and ghost_head_enabled and (len(snake["body"]) >= len(data["you"]["body"])):
				try:
					a[snake["body"][0]["y"]+1][snake["body"][0]["x"]] = 1
				except IndexError:
					pass
				try:
					a[snake["body"][0]["y"]-1][snake["body"][0]["x"]] = 1
				except IndexError:
					pass
				try:
					a[snake["body"][0]["y"]][snake["body"][0]["x"]+1] = 1
				except IndexError:
					pass
				try:
					a[snake["body"][0]["y"]][snake["body"][0]["x"]-1] = 1
				except IndexError:
					pass
	return a

def largestSnake(data):
	"""
	returns true if i am largest snake
	false if otherwise
	"""
	myLength = len(data["you"]["body"])
	for i in data["board"]["snakes"]:
		if i["id"] != data["you"]["id"] and myLength <= len(i["body"]):
			return False
	return True

def findFood(data):
	x = data["you"]["body"][0]["x"]
	y = data["you"]["body"][0]["y"]
	food = data["board"]["food"]
	lowestIndex = 0

	for i in range(len(food)):
		if abs(food[i]["x"]-x)+abs(food[i]["y"]-y) < abs(food[lowestIndex]["x"]-x)+abs(food[lowestIndex]["y"]-y):
			lowestIndex = i

	pos = {"x": food[lowestIndex]["x"], "y": food[lowestIndex]["y"]}
	return pos

def goto(moveC, pos, data):
	"""
	sends snake to position inputted
	"""
	myHeadX = data["you"]["body"][0]["x"]
	myHeadY = data["you"]["body"][0]["y"]
	body_length = len(data["you"]["body"])
	directionX = pos["x"] - myHeadX
	directionY = myHeadY - pos["y"]
	moveX = ""
	moveY = ""
	moveXfill = 0
	moveYfill = 0

	if directionX > 0:
		moveX = "right"
		moveXfill = moveC[2]
	elif directionX < 0:
		moveX = "left"
		moveXfill = moveC[3]
	if directionY > 0:
		moveY = "up"
		moveYfill = moveC[0]
	elif directionY < 0:
		moveY = "down"
		moveYfill = moveC[1]


	if moveXfill == 0 and moveYfill == 0:
		return ""
	if (moveXfill >= body_length) and (moveYfill >= body_length):
		if moveXfill > moveYfill:
			return moveX
		return moveY
	elif (moveXfill >= body_length):
		return moveX
	elif (moveYfill >= body_length):
		return moveY
	else:
		return ""
	#if both have room, return largest
	#else return one with room
	#else return one with largest room


def main():
	bottle.run(
		application,
		host=os.getenv("IP", "0.0.0.0"),
		port=os.getenv("PORT", "8080"),			debug=os.getenv("DEBUG", True),
	)

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == "__main__":
	main()
