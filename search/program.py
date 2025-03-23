# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part A: Single Player Freckers

from re import finditer
from typing import Dict, List
from .core import BOARD_N, CellState, Coord, Direction, MoveAction
from .utils import render_board

# as we are not using the up direction for part a of this project im adding all the avalible directions as a list here
dirPartA = [
        (1, 0),
        (1, 1),
        (1, -1),
        (0, 1),
        (0, -1)]

def search(
    board: dict[Coord, CellState]
) -> list[MoveAction] | None:
    """
    This is the entry point for your submission. You should modify this
    function to solve the search problem discussed in the Part A specification.
    See `core.py` for information on the types being used here.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to "player colours". The keys are `Coord` instances,
            and the values are `CellState` instances which can be one of
            `CellState.RED`, `CellState.BLUE`, or `CellState.LILY_PAD`.
    
    Returns:
        A list of "move actions" as MoveAction instances, or `None` if no
        solution is possible.
    """

    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    print(render_board(board, ansi=True))

    # Do some impressive AI stuff here to find the solution...

    # testing start for vis 1, 3 and 4
    solution = bfsSearch(board, Coord(0, 5))


    # ... (your solution goes here!)
    # ...

    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    return solution
    return [
        MoveAction(Coord(0, 5), [Direction.Down]),
        MoveAction(Coord(1, 5), [Direction.DownLeft]),
        MoveAction(Coord(3, 3), [Direction.Left]),
        MoveAction(Coord(3, 2), [Direction.Down, Direction.Right]),
        MoveAction(Coord(5, 4), [Direction.Down]),
        MoveAction(Coord(6, 4), [Direction.Down]),
    ]

# function that will generate the coordinates of all possible moves a frog can make in a current position
# should take into account if the position is occupied by a frog
# should check if there is a lilypad
# chould check for leeping or multiple leeping
def generatePaths(
        board: dict[Coord, CellState],
        coordinate: Coord
        ) -> list[tuple[Coord, list[Direction]]]: # needs return type
    # retrun list
    coordList:list[tuple[Coord, list[Direction]]] = []

    # check up, down, left, right, down left and down right
    for move in dirPartA:
        try:
            tempCoord = Coord(coordinate.r + move[0], coordinate.c + move[1])
        except:
            continue

        # check that the position exists in the board 
        if tempCoord not in board:
            continue
        

        # check for empty lilypads
        if board.get(tempCoord) == CellState.LILY_PAD:
            # add to list
            dirList = []
            dirList.append(getDirection(coordinate, tempCoord))
            coordList.append((tempCoord, dirList))
            continue

        # all others are frogs
        # check for leeping

        leepingList = checkLeeping(board, tempCoord, coordinate, move, [])
        coordList.extend(leepingList)
    
    return coordList
            

# check for leeping and return all possible coorinates from a leep (eg// leep once or multiple times)
def checkLeeping(
        board: dict[Coord, CellState],
        leepingCoord: Coord,
        previousCoord: Coord,
        dir: tuple[int, int],
        dirListOld: list[Direction]
        ) -> list[tuple[Coord, list[Direction]]]:
    leepingList:list[tuple[Coord, list[Direction]]] = [] 

    # check for valid finish position
    try:
        targetCoord = Coord(leepingCoord.r + dir[0], leepingCoord.c + dir[1])
    except:
        return leepingList

    if targetCoord not in board or board.get(targetCoord) != CellState.LILY_PAD:
        return leepingList

    # add to list 
    dirListOld.append(getDirection(previousCoord, targetCoord))
    leepingList.append((targetCoord, dirListOld.copy()))
    
    # check if further leeping
    for move in dirPartA:
        try: 
            futureLeepingCoord = Coord(targetCoord.r + move[0], targetCoord.c + move[1]) 
            futureTargetCoord = Coord(futureLeepingCoord.r + move[0], futureLeepingCoord.c + move[1]) 
        except:
            continue

        # exlude previous move
        if futureTargetCoord.r == previousCoord.r and futureTargetCoord.c == previousCoord.c:
            continue
        
        # check if jumpable square
        if futureLeepingCoord not in board or board.get(futureLeepingCoord) == CellState.LILY_PAD:
            continue

        # preform leeping list on potenual hit
        # add to direction list
        tempDirList = dirListOld.copy()
        leepingList.extend(checkLeeping(board, futureLeepingCoord, targetCoord, move, tempDirList))

    return leepingList


# bfs search algorithm implimentation 
# must preform bfs as well as keep track of the path
def bfsSearch(
    board: dict[Coord, CellState],
    startCoord: Coord,
) -> list[MoveAction] | None:
    
    # bfs "queue" (coord, direction listing previous transition, previous Coord) pairs
    queue: list[tuple[tuple[Coord, list[Direction]], Coord]] = []
    # list of coordinate key previous coordinate values pairs to reverse engeneer path {Coord: Coord}
    #  None means that it was the start
    record: dict[Coord, tuple[Coord, list[Direction]] | None] = {}

    # add first coordinate to lists
    record[startCoord] = None 

    # solution Coord
    finalCoord = None
    
    # pop first item and generate paths
    possiblePositions = generatePaths(board, startCoord)
    positionsCombined = list(zip(possiblePositions,
                            [startCoord for i in range(len(possiblePositions))])) 
    queue.extend(positionsCombined)

    while len(queue) > 0:
        # pop first item from queue
        position = queue.pop(0) 

        # check if in visited
        if position[0][0] in record:
            continue

        # add to record
        record[position[0][0]] = (position[1], position[0][1]) 

        # check win condition
        if position[0][0].r == BOARD_N -1:
            finalCoord = position[0][0]
            break

        # expand all child nodes
        possiblePositions = generatePaths(board, position[0][0])
        positionsCombined = list(zip(possiblePositions,
                            [position[0][0] for i in range(len(possiblePositions))])) 
        queue.extend(positionsCombined)
    
    # now to reconstruct the solution from the record
    moves:list[MoveAction] = []
   
    # check if a solutionCoord exits
    # if not just return a empty list
    if finalCoord == None:
        return None 

    # need to figure out direction of movement as well
    previousCoord = record[finalCoord]
    
    # loop through until start is reached
    while previousCoord != None:
        moves.append(MoveAction(previousCoord[0], previousCoord[1]))

        # change to next position
        previousCoord = record[previousCoord[0]]
    
    # reversed moves to start from begining
    reversedMoves = moves[::-1]    
    return reversedMoves 

# determine direction of movement from two Coords
def getDirection(startCoord: Coord, endCoord: Coord) -> Direction:
        
    # check down
    if startCoord.r < endCoord.r:
        # check left 
        if startCoord.c > endCoord.c:
            return Direction.DownLeft
        # check right
        if startCoord.c < endCoord.c:
            return Direction.DownRight
        return Direction.Down

    # check left
    if startCoord.c > endCoord.c:
        return Direction.Left

    # check reight 
    return Direction.Right

