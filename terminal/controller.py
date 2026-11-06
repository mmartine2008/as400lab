
import curses
import io
from contextlib import redirect_stdout

from terminal.screen import Screen
from terminal.menu import draw_main_menu
from engine.commands.parser import execute


INPUT_WIDTH = 70
MAX_COMMAND_LENGTH = 512


def show_message(screen, title, message):

    screen.clear()

    screen.write(1, 2, title, screen.yellow)

    lines = message.splitlines()

    for index, line in enumerate(lines[:18]):
        screen.write(3 + index, 2, line)

    screen.write(20, 2, "Press any key to continue...", screen.yellow)

    screen.function_keys()
    screen.refresh()

    screen.stdscr.getch()


def run_terminal(stdscr):

    screen = Screen(stdscr)

    history = []
    current_history = 0
    pending_command = ""

    while True:

        draw_main_menu(screen)

        # Command preloaded by F9 (Retrieve), otherwise empty
        command = pending_command
        pending_command = ""
        cursor = 5 + len(command)

        while True:

            # Horizontal scroll: show the tail of long commands
            offset = max(0, len(command) - (INPUT_WIDTH - 1))
            visible = command[offset:]

            screen.write(19, 5, " " * INPUT_WIDTH)
            screen.write(19, 5, visible)
            screen.stdscr.move(19, 5 + len(visible))
            screen.refresh()

            key = screen.stdscr.getch()

            # F1 - Help
            if key == curses.KEY_F1:

                show_message(
                    screen,
                    "IBM i LAB - HELP",
                    "Type a command and press ENTER.\n"
                    "CRTLIB LIB(name)\n"
                    "WRKLIB\n"
                    "DSPLIB LIB(name)\n"
                    "EXIT"
                )

                break

            # F2 - System status
            elif key == curses.KEY_F2:

                show_message(
                    screen,
                    "SYSTEM STATUS",
                    "IBM i LAB\n"
                    "System: ACTIVE\n"
                    "Environment: Docker/Linux\n"
                    "Database: PostgreSQL\n"
                    "COBOL: GnuCOBOL"
                )

                break

            # F3 - Exit
            elif key == curses.KEY_F3:
                return

            # F4 - Command prompt help
            elif key == curses.KEY_F4:

                show_message(
                    screen,
                    "COMMAND PROMPT",
                    "Examples:\n"
                    "CRTLIB LIB(MILIB)\n"
                    "WRKLIB\n"
                    "DSPLIB LIB(MILIB)\n"
                    "HELP"
                )

                break

            # F5 - Refresh
            elif key == curses.KEY_F5:
                break

            # F9 - Retrieve previous command
            elif key == curses.KEY_F9:

                if history:
                    pending_command = history[-1]

                break

            # F12 - Cancel
            elif key == curses.KEY_F12:
                command = ""
                break

            # ENTER
            elif key in (10, 13, curses.KEY_ENTER):

                if command.strip():

                    history.append(command)
                    current_history = len(history)

                    output = io.StringIO()

                    try:
                        with redirect_stdout(output):
                            running = execute(command)

                    except Exception as error:
                        output.write(f"Error: {error}")
                        running = True

                    if not running:
                        return

                    result = output.getvalue()

                    if result:
                        show_message(
                            screen,
                            "COMMAND OUTPUT",
                            result
                        )

                break

            # Backspace
            elif key in (curses.KEY_BACKSPACE, 127, 8):

                if command:
                    command = command[:-1]
                    cursor = 5 + len(command)

            # Up - Previous command
            elif key == curses.KEY_UP:

                if history and current_history > 0:
                    current_history -= 1
                    command = history[current_history]
                    cursor = 5 + len(command)

            # Down - Next command
            elif key == curses.KEY_DOWN:

                if current_history < len(history) - 1:
                    current_history += 1
                    command = history[current_history]
                    cursor = 5 + len(command)
                else:
                    current_history = len(history)
                    command = ""
                    cursor = 5

            # Printable characters
            elif 32 <= key <= 126:

                if len(command) < MAX_COMMAND_LENGTH:
                    command += chr(key)
                    cursor = 5 + len(command)

