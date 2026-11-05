
import curses

from terminal.controller import run_terminal


def main():
    try:
        curses.wrapper(run_terminal)

    except KeyboardInterrupt:
        pass

    print("\nIBM i LAB session ended.")


if __name__ == "__main__":
    main()

