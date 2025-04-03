# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part A: Single Player Freckers
import math

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

# global varible is here only for testing and comparing the search strategies
bfSexpandedNodes = 0
bfSRepeatedNodes = 0
aStarexpandedNodes = 0

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
    startCoord = findRedFrog(board)
    if startCoord == None:
        return None
    solution1 = aStar(board, startCoord)
    solution2 = bfsSearch(board, startCoord)

    # comarisons
    # solutionEvaluation(solution2, solution1)

    # ... (your solution goes here!)
    # ...

    # Here we're returning "hardcoded" actions as an example of the expected
    # output format. Of course, you should instead return the result of your
    # search algorithm. Remember: if no solution is possible for a given input,
    # return `None` instead of a list.
    return solution1

# -------------------------------------- utility functions -----------------

# find starting coordinate, or the first red frog from the baord 
def findRedFrog(
        board: dict[Coord, CellState],
) -> Coord | None:
    for r in range(BOARD_N):
        for c in range(BOARD_N):
            tempCoord = Coord(r, c)
            # check that it exists
            if tempCoord not in board:
                continue
            if board[tempCoord] == CellState.RED:
                return tempCoord
    return None

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

        # check for leeping
        if board.get(tempCoord) == CellState.BLUE:
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
        if futureLeepingCoord not in board or board.get(futureLeepingCoord) != CellState.BLUE:
            continue

        # preform leeping list on potenual hit
        # add to direction list
        tempDirList = dirListOld.copy()
        leepingList.extend(checkLeeping(board, futureLeepingCoord, targetCoord, move, tempDirList))

    return leepingList


# --------------------------------------- breadth first search ------------------------------

# must preform bfs as well as keep track of the path
# going to use a dictioary the keeps track of each previous move
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
            # global varible for checking how well state checking went
            global bfSRepeatedNodes
            bfSRepeatedNodes += 1
            continue

        # global varible for checking expanded nodes
        global bfSexpandedNodes
        bfSexpandedNodes += 1

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

# ------------------------------------- A* search -------------------------------------------

# A star algorithm
# uses a admissable heuristic based on the minimum number of moves required to get to the end if the problem
# as compressed to one array
def aStar(
        board: dict[Coord, CellState],
        startCoord: Coord        
) -> list[MoveAction] | None:
    
    # a sorted list af all generated positions, with their cost to reach (number of moves) 
    #   current coord, list of directions, previous coord, cost of G(n), cost F(n)
    queue: list[tuple[tuple[Coord, list[Direction]], Coord, int, int]] = []
    # list of coordinate key previous coordinate values pairs to reverse engeneer path {Coord: Coord}
    #  None means that it was the start
    record: dict[Coord, tuple[Coord, list[Direction]] | None] = {}

    # finalCoord, if none then position is unreachable
    finalCoord: Coord | None = None

    # add starting node to the record
    record[startCoord] = None

    # adjaceny array for admissable heuristic
    adjArray = createAdmissableArray(board)

    # push possible positions to queue in sorted order
    queue = addNewAPositions(board, startCoord, 1, queue, adjArray)

    # loop unitl done
    while len(queue) > 0:
         # pop first item from queue
        position = queue.pop(0) 
        
        # remove seen places (needed for cases where ther is no solution)
        if position[0][0] in record:
            continue

        # global vairble to record expanded node
        global aStarexpandedNodes
        aStarexpandedNodes += 1

        # add to record
        record[position[0][0]] = (position[1], position[0][1]) 

        # check win condition
        if position[0][0].r == BOARD_N -1:
            finalCoord = position[0][0]
            break

        # add new items to the queue based on heuristic
        queue = addNewAPositions(board, position[0][0], position[2]+1, queue, adjArray)
 
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


# a method that generates paths from a position, calculates their eitimated cost and inserts them into a soted list
# used for A* and uses admissable heuristic
def addNewAPositions(
        board: dict[Coord, CellState],
        currentCoord: Coord,
        currentCost: int,
        currentList: list[tuple[tuple[Coord, list[Direction]], Coord, int, int]],
        adjArray: list[int]
) -> list[tuple[tuple[Coord, list[Direction]], Coord, int, int]]:
    templist = generatePaths(board, currentCoord)

    # sorry this is a bit of a mess
    # this is using distance to the end as a heuristic
    # this code was the code baing used for the non-admisaable heuristic (distanceToEnd)
     #newPositionsList: list[tuple[tuple[Coord, list[Direction]], Coord, int, int]] = list(zip(templist, [currentCoord for i in range(len(templist))], [currentCost for i in range(len(templist))], [distanceToEnd(entry[0], currentCost) for entry in templist]))

    # this is using the addmissable heuristic
    # combines the next coordinate, direction list, previous coordinate, move cost, and heuristic cost evaluation
    # into a tuple, then puts all of these tuples into a list representing information about all possible moves
    newPositionsList: list[tuple[tuple[Coord, list[Direction]], Coord, int, int]] = list(zip(templist, [currentCoord for i in range(len(templist))], [currentCost for i in range(len(templist))], [admissable(currentCost, adjArray, entry[0]) for entry in templist]))
    newList = currentList.copy()
    
    # to avoid having to search for the lowest heuristic next move every time, we maintain a sorted lsit of all moves
    # and insert in sorted order
    # use a binary search and insert strategy
    if len(newList) == 0:
        newList.append(newPositionsList.pop(0))

    for i in range(len(newPositionsList)):
        upper: int = len(newList)-1
        lower: int = 0

        # check if lower then low bound
        if newPositionsList[i][3] <= newList[lower][3]:
            newList.insert(lower, newPositionsList[i])
            continue

        # check if upper then high bound
        if newPositionsList[i][3] >= newList[upper][3]:
            newList.append(newPositionsList[i])
            continue

        while True:
            temp = math.floor((upper+lower)/2)

            if lower == temp:
                # converged on position therfor insert after
                newList.insert(temp+1, newPositionsList[i])
                break
                
            # check if higher or lower then temp
            if newPositionsList[i][3] > newList[temp][3]:
                lower = temp
                continue 
            if newPositionsList[i][3] < newList[temp][3]:
                upper = temp
                continue 

            # if same then insert before
            if newPositionsList[i][3] == newList[temp][3]:
                newList.insert(temp, newPositionsList[i])
                break

    return newList

# this is a non-deterministic heuristic that we trialed, it is in general faster then the admissable one
# however is not always optimal
# NOT USING IN FINAL SUBMISSION
# A star heuristic, just determine the distance to the end, or number or rows to the end
def distanceToEnd(
        currentCoord: Coord,
        pathCost: int
) -> int:
    return (BOARD_N-1) - currentCoord.r + pathCost 

# admissable a* heuristic, create a array indicating the minimum amoutn of moves required to reach the end
# from a row, use the check if there is a "b" or not
def createAdmissableArray(
    board: dict[Coord, CellState]
) -> list[int]:
    # create list of minimum number of moves
    numberOfMoves = [0 for i in range(BOARD_N)]

    # list of which rows contain a blue frog
    blueFrogList = [0 for i in range(BOARD_N)]

    # populate blue frog list
    for i in range(BOARD_N):
        for j in range(BOARD_N):
            tempCoord = Coord(i, j)
            if tempCoord in board and board[tempCoord] == CellState.BLUE:
                blueFrogList[i] = 1
                break;

    # for each row, check the how many possible jumps eg (if blueFrogList = 0, 1, 0, 1, 1, 1, 0) its only one move to the end

    for i in range(BOARD_N):
        j = i 
        moves = 0
        jump = 0
        while j+1 < BOARD_N:
            if j+2 < BOARD_N and blueFrogList[j+1] == 1:
                # can jump
                j += 2
                if jump == 0:
                    jump = 1
                    moves += 1
                continue
            # cant jump therfore simply move
            jump = 0
            j += 1
            moves += 1
        numberOfMoves[i] = moves

    return numberOfMoves

def admissable(
        pathCost: int,
        adjArray: list[int],
        currentCoord: Coord
) -> int:
    return pathCost + adjArray[currentCoord.r] 
 

# ------------------------------------------ for determineing algorithm efficiency -------------------

# function that is for personal analysis of algorithms
# and assistance in report
def solutionEvaluation(solutionBfs, solutionAstar):
    # compare solutions
    print("Solution for BFS:")
    # print_result(solutionBfs)
    print("\n\n---------------------------------------------\n\n")
    print("Solution for A*:")
    # print_result(solutionAstar)
    print("\n\n---------------------------------------------\n\n")

    print("BFS analysis:")
    print(f"Number of expanded Nodes: {bfSexpandedNodes}")
    print(f"Number of repeated Nodes blocked by repeated state checking: {bfSRepeatedNodes}")

    print("\n\n---------------------------------------------\n\n")
    print("A* analysis")
    print(f"Number of expanded Nodes: {aStarexpandedNodes}")
    print("\n\n---------------------------------------------\n\n")
    


