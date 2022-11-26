import json
import os
import random

def info():
    print("INFO")

    return ({
        "apiversion": "1",
        "author": "Nathaniel Roberts",
        "color": "#000000",
        "head": "default",
        "tail": "default"
    })

def index():
    return "Your Battlesnake is alive!"

def start(game_state):
    """
    Called every time a new Battlesnake game starts and your snake is in it.
    Your response will control how your snake is displayed on the board.
    """
    print("GAME START")
    
def move(game_state):
    """
    Called when the Battlesnake Engine needs to know your next move.
    The data parameter will contain information about the board.
    Your response must include your move of up, down, left, or right.
    """

    data = game_state
    move = ""
    up_area = floodFill(getNextPosition("up", data), data, arrayify(data, not largestSnake(data)))
    down_area = floodFill(getNextPosition("down", data), data, arrayify(data, not largestSnake(data)))
    right_area = floodFill(getNextPosition("right", data), data, arrayify(data, not largestSnake(data)))
    left_area = floodFill(getNextPosition("left", data),  data, arrayify(data, not largestSnake(data)))
    move_area = [up_area, down_area, right_area, left_area]

    if len(data["board"]["food"]) > 0:
        print("My Current position: {}".format(data["you"]["head"]))
        print("Closest Food: {}".format(findFood(data)))
        move = goto(move_area, findFood(data), data)

    if is_stuck(move_area, data) and max(move_area) != 0:
        if up_area == max(move_area):
            move = "up"
        elif down_area == max(move_area):
            move = "down"
        elif left_area == max(move_area):
            move = "left"
        elif right_area == max(move_area):
            move = "right"

    if max(move_area) == 0:
        print("disabling ghostheads no good moves detected")
        up_area = floodFill(getNextPosition("up", data), data, arrayify(data, False))
        down_area = floodFill(getNextPosition("down", data), data, arrayify(data, False))
        right_area = floodFill(getNextPosition("right", data), data, arrayify(data, False))
        left_area = floodFill(getNextPosition("left", data),  data, arrayify(data, False))
        move_area = [up_area, down_area, right_area, left_area]

    print(up_area, down_area, right_area, left_area)
    if move == "":
        goodMoves = []
        if up_area == max(move_area):
            goodMoves.append("up")
        if down_area == max(move_area):
            goodMoves.append("down")
        if left_area == max(move_area):
            goodMoves.append("left")
        if right_area == max(move_area):
            goodMoves.append("right")
        move = random.choice(goodMoves)
    print(move)
    return {"move": move}
    

def end(game_state):
    """
    Called every time a game with your snake in it ends.
    """
    print("GAME OVER")
    

def is_stuck(move_area, data):
    body_length = len(data["you"]["body"])
    if max(move_area) < body_length:
        return True
    return False


def getNextPosition(move, data):
    """
    returns next position depending on which inputted
    """
    nextPos = {"x": data["you"]["head"]['x'],
                "y": data["you"]["head"]['y']}

    if move == 'up':
        nextPos["y"] = nextPos["y"] + 1
    elif move == 'down':
        nextPos["y"] = nextPos["y"] - 1
    elif move == 'right':
        nextPos["x"] = nextPos["x"] + 1
    elif move == 'left'	:
        nextPos["x"] = nextPos["x"] - 1
    return nextPos


#if cords are not within the board, return false else return true
def is_cords_in_board(x, y, height, width):
    if x < 0 or x > width - 1:
        return False
    if y < 0 or y > height - 1:
        return False
    return True

def is_occupied(x, y, dataArray):
    game_width = len(dataArray)
    game_height = len(dataArray[0])
    if not is_cords_in_board(x, y, game_height, game_width):
        return True
    elif dataArray[x][y] == 1:
        return True
    return False 

def floodFill(pos, data, dataArray):
    """
    checks how much room there is if snake does a move
    used so snake doesn't run into a corner
    returns free space
    """
    count = 0
    if is_occupied(pos["x"], pos["y"], dataArray):
        return count
    
    # mark node as visited
    dataArray[pos["x"]][pos["y"]] = 1
    
    count += 1
    count += floodFill({"x": pos["x"], "y": pos["y"]-1}, data, dataArray)
    count += floodFill({"x": pos["x"], "y": pos["y"]+1}, data, dataArray)
    count += floodFill({"x": pos["x"]-1, "y": pos["y"]}, data, dataArray)
    count += floodFill({"x": pos["x"]+1, "y": pos["y"]}, data, dataArray)
    
    return count

def arrayify(data, ghost_heads: bool):
    height = data["board"]["height"]
    width = data["board"]["width"]

    array = [[0] * height for i in range(width)]

    snakes = data["board"]["snakes"]
    for snake in snakes:
        for body_part in snake["body"]:
            array[body_part["x"]][body_part["y"]] = 1
    if ghost_heads:
        for snake in snakes:
            if snake["id"] == data["you"]["id"]:
                continue
            head_x = snake["head"]["x"]
            head_y = snake["head"]["y"]
            if is_cords_in_board(head_x-1, head_y, height, width):
                array[head_x-1][head_y] = 1
            if is_cords_in_board(head_x+1, head_y, height, width):
                array[head_x+1][head_y] = 1
            if is_cords_in_board(head_x, head_y-1, height, width):
                array[head_x][head_y-1] = 1
            if is_cords_in_board(head_x, head_y+1, height, width):
                array[head_x][head_y+1] = 1
    return array

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
    x = data["you"]["head"]["x"]
    y = data["you"]["head"]["y"]
    food = data["board"]["food"]
    closest_food = data["board"]["food"][0]
    for food in data["board"]["food"]:
        distance_x = abs(x - food["x"])
        distance_y = abs(y - food["y"])
        delta_distance = distance_x + distance_y
        current_closest_distance = abs(x - closest_food["x"]) + abs(y - closest_food["y"])
        if delta_distance < current_closest_distance:
            closest_food = food
    return closest_food

def goto(move_area, pos, data):
    """
    sends snake to position inputted
    """
    body_length = len(data["you"]["body"])

    my_head_x = data["you"]["head"]["x"]
    my_head_y = data["you"]["head"]["y"] 

    distance_x = my_head_x - pos["x"]
    distance_y = my_head_y - pos["y"]

    move_x = ""
    move_x_area = 0
    if distance_x > 0:
        move_x = "left"
        move_x_area = move_area[3]
    elif distance_x < 0:
        move_x = "right"
        move_x_area = move_area[2]
    move_y = ""
    move_y_area = 0
    if distance_y > 0:
        move_y = "down"
        move_y_area = move_area[1]
    elif distance_y < 0:
        move_y = "up"   
        move_y_area = move_area[0] 

    if move_x_area < body_length:
        move_x_area = 0
        move_x = ""
    if move_y_area < body_length:
        move_y_area = 0
        move_y = ""
    print("MOVE X: {}".format(move_x))
    print("MOVE Y: {}".format(move_y)) 
    # if there are no valid moves, return "".  if one of the moves is invalid, return the other.  if both are valid choose move with most area
    if move_y == "" and move_x == "":
        return ""
    elif move_y == "":
        return move_x
    elif move_x == "":
        return move_y
    elif move_x_area > move_y_area:
        return move_x
    elif move_y_area > move_x_area:
        return move_y
    else:
        return random.choice([move_x, move_y]) 

if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
 