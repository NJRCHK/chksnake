# chksnake
battlesnake is a coding competition where contestants create programs capable of playing snake. these snakes are put into the same arena and must battle. all rules found at https://docs.battlesnake.com/

chksnake uses floodfill to evaluate moves, and situational ghostheads to avoid head on collisions when necessary. if it detects that it is stuck (in an area with less space than the length of the snake), it will move in a pattern to maximize area used.  
