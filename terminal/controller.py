
import curses
import io
from contextlib import redirect_stdout

from terminal.screen import Screen
from terminal.menu import draw_main_menu
from engine.commands.parser import execute


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

    while True:

        draw_main_menu(screen)

        command = ""
        cursor = 5

        while True:

            screen.write(19, 5, " " * 70)
            screen.write(19, 5, command)
            screen.stdscr.move(19, 5 + cursor - 5)
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
                    command = history[-1]
                    cursor = 5 + len(command)

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

                if len(command) < 70:
                    command += chr(key)
                    cursor = 5 + len(command)

