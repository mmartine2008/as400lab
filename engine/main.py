
from engine.commands.parser import execute


def main():
    print()
    print("======================================")
    print("             IBM i LAB")
    print("======================================")
    print()
    print("  Educational IBM i Simulator")
    print("  System status: ACTIVE")
    print()
    print("  Type HELP for available commands.")
    print()

    running = True

    while running:
        try:
            command = input("===> ")
            running = execute(command)

        except KeyboardInterrupt:
            print("\nUse EXIT to leave the system.")

        except EOFError:
            running = False

        except Exception as error:
            print(f"System error: {error}")

    print()
    print("IBM i LAB session ended.")
    print()


if __name__ == "__main__":
    main()

