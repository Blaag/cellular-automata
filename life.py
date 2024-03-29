import curses
from curses import wrapper
import random
import time
import json
import copy

# Global items
CURSOR_VISIBILITY = 0
GAMEBOARD_HEIGHT = 35
GAMEBOARD_WIDTH = 160
INFOBOARD_WIDTH = 40
INITIAL_GAME_SPEED = 1
# ALIVE_CHARACTER = '\u2588' # full block
# ALIVE_CHARACTER = '\u25ef' # circle
# ALIVE_CHARACTER = '\u041e' # cyrillic capital O
ALIVE_CHARACTER = '\u25fb' # white medium square
# ALIVE_CHARACTER = '\u26aa' # white circle, breaks monospace
# DEAD_CHARACTER = '.'
DEAD_CHARACTER = ' '
SCREEN_UPDATE_INTERVAL = 5000 # how fast the information window updates, lower = faster
GAME_UPDATE_INTERVAL = 500000 # how fast the game runs initially, lower = faster, user can change in game

def seed_board(gameboard_height, gameboard_width):
    # This function is responsible for seeding the
    # game board with random live cells
    board = []

    for y in range(0, gameboard_height):
        for x in range(0, gameboard_width):
            alive_digit = random.randint(0, 1)

            if alive_digit == 1:
                alive = True
                display_character = ALIVE_CHARACTER
                rounds_alive = 1
            else:
                alive = False
                display_character = DEAD_CHARACTER
                rounds_alive = 0

            cell = {
                "alive_bool": alive, # for easy if/thens
                "alive_digit": alive_digit, # for easy debugging
                "display_character": display_character, # for more interesting visuals by other criteria
                "rounds_alive": rounds_alive # how long a cell has been alive consecutively - goes to 0 on death
            }
            board.append(cell)

    return board

def fill_pad_with_gameboard(height, width, gameboard, p):
    # Copies the gameboard into a pad that can be
    # displayed on-screen.
    for y in range(0, height):
        for x in range(0, width):
            gameboard_char = gameboard[x + (y * width)]["display_character"]
            try:
                p.addstr(y, x, f'{gameboard_char}')
            except curses.error: # need this for writing to bottom right corner, lame
                pass
    return p

def count_neighbors(y, x, gameboard, win):
    # Count the number of neighbors a given cell has.
    # This is used to determine whether a cell lives, dies,
    # or is born.
    
    neighbor_count = 0
    check_positions = [
        [-1, -1], # top left
        [-1, 0],  # top middle
        [-1, 1],  # top right
        [0, -1],  # middle left
        [0, 1],   # middle right
        [1, -1],  # bottom left
        [1, 0],   # bottom middle
        [1, 1]    # bottom right
    ]

    # Below is a bunch of debugging code to help
    # determine whether neighbors are being counted
    # correctly and whether arrays are wrapping
    # at the edges.
    
    # check_indexes = []
    
    # Display the coords being examined
    # for i in range(3):
    #     x_pos = (x + check_positions[i][1]) % GAMEBOARD_WIDTH
    #     y_pos = (y + check_positions[i][0]) % GAMEBOARD_HEIGHT
    #     win.addstr(10, 1 + i * 5, f'{y_pos},{x_pos}')
    # for i in range(2):
    #     x_pos = (x + check_positions[3 + i][1]) % GAMEBOARD_WIDTH
    #     y_pos = (y + check_positions[3 + i][0]) % GAMEBOARD_HEIGHT
    #     win.addstr(11, 1 + (2 * i) * 5, f'{y_pos},{x_pos}')
    # win.addstr(11, 6, f'{y},{x}')
    # for i in range(3):
    #     x_pos = (x + check_positions[5 + i][1]) % GAMEBOARD_WIDTH
    #     y_pos = (y + check_positions[5 + i][0]) % GAMEBOARD_HEIGHT
    #     win.addstr(12, 1 + i * 5, f'{y_pos},{x_pos}')

    # Display the cells being examined
    # for i in range(3):
    #     x_pos = (x + check_positions[i][1]) % GAMEBOARD_WIDTH
    #     y_pos = (y + check_positions[i][0]) % GAMEBOARD_HEIGHT
    #     win.addstr(14, 1 + i * 5, f'{gameboard[x_pos + (y_pos * GAMEBOARD_WIDTH)]["alive_digit"]}')
    # for i in range(2):
    #     x_pos = (x + check_positions[3 + i][1]) % GAMEBOARD_WIDTH
    #     y_pos = (y + check_positions[3 + i][0]) % GAMEBOARD_HEIGHT
    #     win.addstr(15, 1 + (2 * i) * 5, f'{gameboard[x_pos + (y_pos * GAMEBOARD_WIDTH)]["alive_digit"]}')
    # win.addstr(15, 6, f'{gameboard[x + (y * x)]["alive_digit"]}')
    # for i in range(3):
    #     x_pos = (x + check_positions[5 + i][1]) % GAMEBOARD_WIDTH
    #     y_pos = (y + check_positions[5 + i][0]) % GAMEBOARD_HEIGHT
    #     win.addstr(16, 1 + i * 5, f'{gameboard[x_pos + (y_pos * GAMEBOARD_WIDTH)]["alive_digit"]}')

    # Display indexes being examined
    # for i in range(3):
    #     x_pos = (x + check_positions[i][1]) % GAMEBOARD_WIDTH
    #     y_pos = (y + check_positions[i][0]) % GAMEBOARD_HEIGHT
    #     win.addstr(18, 1 + i * 5, f'{x_pos + (y_pos * GAMEBOARD_WIDTH)} ')
    #     check_indexes.append(x_pos + (y_pos * GAMEBOARD_WIDTH))
    # for i in range(2):
    #     x_pos = (x + check_positions[3 + i][1]) % GAMEBOARD_WIDTH
    #     y_pos = (y + check_positions[3 + i][0]) % GAMEBOARD_HEIGHT
    #     win.addstr(19, 1 + (2 * i) * 5, f'{x_pos + (y_pos * GAMEBOARD_WIDTH)} ')
    #     check_indexes.append(x_pos + (y_pos * GAMEBOARD_WIDTH))
    # win.addstr(19, 6, f'{x + (y * GAMEBOARD_WIDTH)} ')
    # for i in range(3):
    #     x_pos = (x + check_positions[5 + i][1]) % GAMEBOARD_WIDTH
    #     y_pos = (y + check_positions[5 + i][0]) % GAMEBOARD_HEIGHT
    #     check_indexes.append(x_pos + (y_pos * GAMEBOARD_WIDTH))
    #     win.addstr(20, 1 + i * 5, f'{x_pos + (y_pos * GAMEBOARD_WIDTH)} ')

    # win.addstr(21, 1, f'idx:{check_indexes} ')

    for coords in check_positions:
        x_pos = (x + coords[1]) % GAMEBOARD_WIDTH # Python's modulus works with negative numbers to wrap!
        y_pos = (y + coords[0]) % GAMEBOARD_HEIGHT
        # win.addstr(23, 1, f'checking gameboard index of {x + (y * GAMEBOARD_WIDTH)} ')
        if gameboard[x_pos + (y_pos * GAMEBOARD_WIDTH)]["alive_bool"]:
            neighbor_count += 1

    return neighbor_count

def display_character(rounds_alive):
    # Testing out ways to visualize how long cells have
    # been alive
    if rounds_alive <= 20:
        # subtract one from rounds_alive because \u2460 is already a "1"
        return chr(ord('\u2460') + rounds_alive - 1)
    else:
        return ALIVE_CHARACTER
        # return '\004F'

def get_tick_char(current_tick_char):
    # This function advances the tick character
    # so that it is obvious the game is running
    # and that you have a visual sense of game
    # speed
 
    match current_tick_char:
        case '|':
            return '/'
        case '/':
            return '-'
        case '-':
            return '\\'
        case '\\':
            return '|'
    
def init_settings_dict(screen):
    # Configure a dictionary that contains all
    # information that is changeable or computed
    # and will be be displayed on the info pane.

    # Get the screen height, width
    term_height, term_width = screen.getmaxyx()

    settings_dict = {
        "game_running": True, # for determining whether the simulation is paused or running
        "game_round": 1, # how many rounds of the game we've went through
        "tick": 0, # how many cycles we have went through running the game, checking for keypresses, etc
        "tick_character": '|', # initial character for giving a visual representation of the game running and at what speed
        "speed": INITIAL_GAME_SPEED, # how fast the game should run (higher = faster), at some point higher won't be faster
        "term_height": term_height, # total terminal screen height
        "term_width": term_width, # total terminal screen width
        "gameboard_window_start_y": 1, # account for the border around the pad
        "gameboard_window_start_x": INFOBOARD_WIDTH + 1, # account for the border around the pad
        "gameboard_window_stop_y": term_height - 2, # at what row we stop showing the game board, account for the border around the pad
        "gameboard_window_stop_x": term_width, # at what column we stop showing the game board
        "gameboard_text_color": "RED_ON_BLACK",
        "gameboard_border_color": "GREEN",
        "infoboard_text_color": "GREY",
        "infoboard_border_color": "GREEN"
    }

    return settings_dict

def init_stats_dict():
    # Configure a dictionary that contains all
    # information that is static and will be
    # be displayed on the info pane.

    stats_dict = {
        "game_round_cell_births": 0,
        "game_round_cell_deaths": 0,
        "game_round_cell_sustains": 0,
        "game_round_num_changes": 0,
        "game_total_cell_births": 0,
        "game_total_cell_deaths": 0,
        "game_total_cell_sustains": 0,
        "game_total_num_changes": 0
    }

    return stats_dict

def setup(screen, speed = 1):
    # Does all things to set up the game.
    # Used initially, and then used
    # whenever the user wants to start
    # a new game.
    #
    # gameboard_stats = array of info about the game, tracks cells and cell metadata
    # gameboard_settings = dict of settings about the gameboard
    # infoboard_win = window that displays commands and stats about the game
    # gameboard_win = a window that exists solely to add a border around the pad
    # p = a pad that creates a visual representation of the gameboard

    # Create and seed the board with random live cells
    gameboard = seed_board(GAMEBOARD_HEIGHT, GAMEBOARD_WIDTH)

    # Generate starting settings and stats
    gameboard_stats = init_stats_dict()
    gameboard_settings = init_settings_dict(screen)
    gameboard_settings["speed"] = speed # if the user resets the game, don't reset the speed
    infoboard_win = curses.newwin(gameboard_settings["term_height"], INFOBOARD_WIDTH, 0, 0) # Infoboard window
    gameboard_win = curses.newwin(gameboard_settings["term_height"], gameboard_settings["term_width"] - INFOBOARD_WIDTH - 2, 0, INFOBOARD_WIDTH + 1)
    p = curses.newpad(GAMEBOARD_HEIGHT, GAMEBOARD_WIDTH) # Create a pad to visually show the gameboard
    fill_pad_with_gameboard(GAMEBOARD_HEIGHT, GAMEBOARD_WIDTH, gameboard, p) # Fill pad with cells from gameboard

    return gameboard, gameboard_stats, gameboard_settings, infoboard_win, gameboard_win, p

def main(screen):
    # Runs the game
    
    # Initial values for things that must be set
    key = None # for checking keypresses
    px_coord = 0 # y value for where to start viewing the pad
    py_coord = 0 # x value for where to start viewing the pad
    game_state = "running" # Textual representation of the boolean game state

    # Curses specific items
    #
    # 1) Turn echo off so that keypresses don't briefly appear
    # 2) Make the cursor not visible
    # 3) Enable color if we can
    # 4) Use default colors so black is black and not greyish
    # 5) Turn on non-blocking checks for keypresses
    curses.noecho()
    curses.curs_set(CURSOR_VISIBILITY)
    if curses.has_colors():
        curses.start_color()
    curses.use_default_colors()
    screen.nodelay(True)

    # Run the initial setup of creating windows, populating default values, etc
    gameboard, gameboard_stats, gameboard_settings, infoboard_win, gameboard_win, p = setup(screen)

    # Loop through the game until it's time to quit
    while key != 'q':
        # See if there's a keypress
        try:
            key = screen.getkey()
        except:
            key = None # We are using nodelay, so set the key to None if nothing was pressed

        # Increment the game tick
        gameboard_settings["tick"] += 1

        # Reset timers on game board and info board
        game_board_total_time = 0
        infoboard_total_time = 0

        # See if it's time to run a round of the game
        if (gameboard_settings["tick"] % int(GAME_UPDATE_INTERVAL / (2 * gameboard_settings["speed"])) == 0):

            # Grab the current time so we can know how long this takes
            game_round_start_time = time.time()

            # Advance the tick character to show we are running, as long as we are not paused
            if gameboard_settings["game_running"]:
                gameboard_settings["tick_character"] = get_tick_char(gameboard_settings["tick_character"])
                infoboard_win.box()

            # Show the border around the gameboard            
            gameboard_win.box()
            gameboard_win.noutrefresh()

            # Show the gameboard - important to do this before we compute the next generation
            p.noutrefresh(
                py_coord,
                px_coord,
                gameboard_settings["gameboard_window_start_y"],
                gameboard_settings["gameboard_window_start_x"] + 1, # to account for border on gameboard
                gameboard_settings["gameboard_window_stop_y"],
                gameboard_settings["gameboard_window_stop_x"] - 3 # why?
            )

            # Determine the next generation
            if gameboard_settings["game_running"]:

                # reset per-round stats
                gameboard_stats["game_round_cell_births"] = 0
                gameboard_stats["game_round_cell_deaths"] = 0
                gameboard_stats["game_round_cell_sustains"] = 0
                gameboard_stats["game_round_num_changes"] = 0

                # Make a copy of the gameboard that can be modified
                new_gameboard = copy.deepcopy(gameboard)
                
                # Go through each cell and determine whether they live, die, or become alive
                for y in range(GAMEBOARD_HEIGHT):
                    for x in range(GAMEBOARD_WIDTH):
                        neighbors = count_neighbors(y, x, gameboard, infoboard_win)
                        # infoboard_win.addstr(5, 1, f'Position {y}, {x} has {neighbors} neighbors.  ')
                        if (gameboard[x + (y * GAMEBOARD_WIDTH)]["alive_bool"]) and (neighbors >= 2 and neighbors <= 3): # existing cell stays alive
                            new_gameboard[x + (y * GAMEBOARD_WIDTH)]["rounds_alive"] += 1
                            new_gameboard[x + (y * GAMEBOARD_WIDTH)]["display_character"] = display_character(new_gameboard[x + (y * GAMEBOARD_WIDTH)]["rounds_alive"])
                            gameboard_stats["game_round_cell_sustains"] += 1
                        elif (not gameboard[x + (y * GAMEBOARD_WIDTH)]["alive_bool"]) and (neighbors == 3): # new cell arises
                            new_gameboard[x + (y * GAMEBOARD_WIDTH)]["alive_bool"] = True
                            new_gameboard[x + (y * GAMEBOARD_WIDTH)]["alive_digit"] = 1
                            # new_gameboard[x + (y * GAMEBOARD_WIDTH)]["display_character"] = ALIVE_CHARACTER
                            new_gameboard[x + (y * GAMEBOARD_WIDTH)]["rounds_alive"] = 1
                            new_gameboard[x + (y * GAMEBOARD_WIDTH)]["display_character"] = display_character(1)
                            gameboard_stats["game_round_num_changes"] += 1
                            gameboard_stats["game_round_cell_births"] += 1
                        # in all other cases the cell stays dead or dies but we will track it for stats
                        elif gameboard[x + (y * GAMEBOARD_WIDTH)]["alive_bool"]: # cell was alive but died due to loneliness or crowding
                            new_gameboard[x + (y * GAMEBOARD_WIDTH)]["alive_bool"] = False
                            new_gameboard[x + (y * GAMEBOARD_WIDTH)]["alive_digit"] = 0
                            new_gameboard[x + (y * GAMEBOARD_WIDTH)]["rounds_alive"] = 0
                            new_gameboard[x + (y * GAMEBOARD_WIDTH)]["display_character"] = DEAD_CHARACTER
                            gameboard_stats["game_round_num_changes"] += 1
                            gameboard_stats["game_round_cell_deaths"] += 1
                        else:
                            # Cell is already dead
                            pass
                            
                gameboard_settings["game_round"] += 1
                gameboard = copy.deepcopy(new_gameboard)
                fill_pad_with_gameboard(GAMEBOARD_HEIGHT, GAMEBOARD_WIDTH, new_gameboard, p)
                # del new_gameboard

                curses.doupdate()

            # Grab the end time so we can know how long this takes
            game_round_total_time = time.time() - game_round_start_time
            
        if key != None:
            match key:
                case 'w': # move viewport up
                    py_coord = max(0, py_coord - 1)
                    p.noutrefresh(
                        py_coord,
                        px_coord,
                        gameboard_settings["gameboard_window_start_y"],
                        gameboard_settings["gameboard_window_start_x"] + 1, # to account for border on gameboard
                        gameboard_settings["gameboard_window_stop_y"],
                        gameboard_settings["gameboard_window_stop_x"] - 3 # why?
                    )
                case 'a': # move viewport left
                    px_coord = max(0, px_coord - 1)
                    p.noutrefresh(
                        py_coord,
                        px_coord,
                        gameboard_settings["gameboard_window_start_y"],
                        gameboard_settings["gameboard_window_start_x"] + 1, # to account for border on gameboard
                        gameboard_settings["gameboard_window_stop_y"],
                        gameboard_settings["gameboard_window_stop_x"] - 3 # why?
                    )
                case 's': # move viewport down
                    # py_coord += 1
                    py_coord = min(GAMEBOARD_HEIGHT - 1, py_coord + 1)
                    p.noutrefresh(
                        py_coord,
                        px_coord,
                        gameboard_settings["gameboard_window_start_y"],
                        gameboard_settings["gameboard_window_start_x"] + 1, # to account for border on gameboard
                        gameboard_settings["gameboard_window_stop_y"],
                        gameboard_settings["gameboard_window_stop_x"] - 3 # why?
                    )
                case 'd': # move viewport right
                    # px_coord += 1
                    px_coord = min(GAMEBOARD_WIDTH - 1, px_coord + 1)
                    p.noutrefresh(
                        py_coord,
                        px_coord,
                        gameboard_settings["gameboard_window_start_y"],
                        gameboard_settings["gameboard_window_start_x"] + 1, # to account for border on gameboard
                        gameboard_settings["gameboard_window_stop_y"],
                        gameboard_settings["gameboard_window_stop_x"] - 3 # why?
                    )
                case 'p': # pause/unpause the game
                    gameboard_settings["game_running"] = not gameboard_settings["game_running"] # toggle pause/unpause
                    if gameboard_settings["game_running"]:
                        game_state = "running"
                    else:
                        game_state = "paused"
                    p.noutrefresh(
                        py_coord,
                        px_coord,
                        gameboard_settings["gameboard_window_start_y"],
                        gameboard_settings["gameboard_window_start_x"] + 1, # to account for border on gameboard
                        gameboard_settings["gameboard_window_stop_y"],
                        gameboard_settings["gameboard_window_stop_x"] - 3 # why?
                    )
                case '+': # speed up the game
                    gameboard_settings["speed"] += 1
                case '=': # speed up the game
                    gameboard_settings["speed"] += 1
                case 'r': # reset the game
                    gameboard, gameboard_stats, gameboard_settings, infoboard_win, gameboard_win, p = setup(screen, gameboard_settings["speed"])
                case '-': # slow down the game
                    gameboard_settings["speed"] = max(1, gameboard_settings["speed"] - 1) # speed cant be less than 1

        # Do screen update items - only run these once in a while
        # so that cpu can be spent running the simulation instead of screen updates
        if (gameboard_settings["tick"] % SCREEN_UPDATE_INTERVAL) == 0:
            # Grab the current time so we can know how long this takes
            infoboard_start_time = time.time()

            # Interesting data
            infoboard_win.addstr(1, 1, f'Game is {game_state} at speed: {gameboard_settings["speed"]}  ')
            infoboard_win.addstr(1, 35, f'{gameboard_settings["tick_character"]}')
            infoboard_win.addstr(2, 1, f'Screen size (y,x): {gameboard_settings["term_height"]},{gameboard_settings["term_width"]}')
            infoboard_win.addstr(3, 1, f'Gameboard size (y,x): {GAMEBOARD_HEIGHT},{GAMEBOARD_WIDTH}')
            infoboard_win.addstr(4, 1, f'Gameboard view offset (y,x): {py_coord},{px_coord}  ')
            infoboard_win.addstr(5, 1, f'Game round: {gameboard_settings["game_round"]}  ')
            infoboard_win.addstr(7, 1, f'Round has {gameboard_stats["game_round_num_changes"]} changes.   ')
            infoboard_win.addstr(8, 1, f'  Cell births: {gameboard_stats["game_round_cell_births"]}  ')
            infoboard_win.addstr(9, 1, f'  Cell deaths: {gameboard_stats["game_round_cell_deaths"]}  ')
            infoboard_win.addstr(10, 1, f'  Cells staying living: {gameboard_stats["game_round_cell_sustains"]}  ')

            # Help / commands
            infoboard_win.addstr(gameboard_settings["term_height"] - 7, 1, f'Commands:')
            infoboard_win.addstr(gameboard_settings["term_height"] - 6, 1, f'WASD = Move game viewport')
            infoboard_win.addstr(gameboard_settings["term_height"] - 5, 1, f'p = Pause/unpause game')
            infoboard_win.addstr(gameboard_settings["term_height"] - 4, 1, f'r = Reset game')
            infoboard_win.addstr(gameboard_settings["term_height"] - 3, 1, f'+/- = Speed up or slow down game')
            infoboard_win.addstr(gameboard_settings["term_height"] - 2, 1, f'q = Quit')
            infoboard_win.noutrefresh()

            # Grab the end time so we can know how long this takes
            infoboard_total_time = time.time() - infoboard_start_time
            
        total_time = game_board_total_time + infoboard_total_time
        # if total_time > 0 and total_time < 1: # only sleep if we were actually doing something
        #     time.sleep(total_time % 1) # sleep the remainder of a second
            
        if key != None:
            curses.doupdate()

    curses.endwin()
    print(f'Share and enjoy!')

if __name__ == "__main__":
    wrapper(main)
