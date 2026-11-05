
def draw_main_menu(screen):

    screen.clear()

    screen.write(0, 0, "IBM i LAB", screen.yellow)
    screen.write(0, 60, "SYSTEM: ACTIVE", screen.green)

    screen.write(2, 24, "IBM i LAB - MAIN MENU", screen.white)

    options = [
        "1. User tasks",
        "2. Office tasks",
        "3. General system tasks",
        "4. Files, libraries and folders",
        "5. Programming",
        "6. Communications",
        "7. Define or change the system",
        "8. Problem handling",
        "9. Display a menu"
    ]

    screen.write(5, 5, "Select one of the following:")

    for index, option in enumerate(options):
        screen.write(7 + index, 10, option)

    screen.write(18, 0, "Selection or command")
    screen.write(19, 0, "===> ")

    screen.function_keys()
    screen.refresh()

