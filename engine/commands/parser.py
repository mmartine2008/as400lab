
import re

import subprocess
from pathlib import Path

from engine.objects.file_manager import (
    create_physical_file,
    create_logical_file,
    display_file_description,
    display_file_fields
)

from engine.libraries.manager import (
    create_library,
    list_libraries,
    display_library
)


def get_parameter(command, parameter):
    pattern = rf"\b{parameter}\s*\(\s*([^)]*)\s*\)"
    match = re.search(pattern, command, re.IGNORECASE)

    if match:
        return match.group(1).strip().strip("'\"")

    return None


def execute(command):
    command = command.strip()

    if not command:
        return True

    upper = command.upper()

    # CRTLIB LIB(MYLIB)

    if upper.startswith("CRTLIB"):
        name = get_parameter(command, "LIB")

        if not name:
            print("Required parameter LIB missing.")
        else:
            create_library(name)

        return True

    # WRKLIB

    if upper == "WRKLIB" or upper.startswith("WRKLIB "):
        name = command[6:].strip()

        if name:
            display_library(name)
        else:
            list_libraries()

        return True

    # DSPLIB LIB(MYLIB)

    if upper.startswith("DSPLIB"):
        name = get_parameter(command, "LIB")

        if name:
            display_library(name)
        else:
            print("Required parameter LIB missing.")

        return True


    # CRTPF FILE(LIBRARY/FILE) FIELDS(...)

    if upper.startswith("CRTPF"):
        file_name = get_parameter(command, "FILE")
        fields = get_parameter(command, "FIELDS")

        if not file_name or not fields:
            print("Required parameters FILE and FIELDS missing.")
        else:
            create_physical_file(file_name, fields)

        return True

    # CRTLF FILE(...) BASE(...) ORDERBY(...)

    if upper.startswith("CRTLF"):
        file_name = get_parameter(command, "FILE")
        base_file = get_parameter(command, "BASE")
        order_by = get_parameter(command, "ORDERBY")

        if not file_name or not base_file or not order_by:
            print("Required parameters FILE, BASE and ORDERBY missing.")
        else:
            create_logical_file(file_name, base_file, order_by)

        return True

    # DSPFD FILE(...)

    if upper.startswith("DSPFD"):
        file_name = get_parameter(command, "FILE")

        if file_name:
            display_file_description(file_name)
        else:
            print("Required parameter FILE missing.")

        return True

    # DSPFFD FILE(...)

    if upper.startswith("DSPFFD"):
        file_name = get_parameter(command, "FILE")

        if file_name:
            display_file_fields(file_name)
        else:
            print("Required parameter FILE missing.")

        return True
        
    # -------------------------------------------------
    # CALL PROGRAM
    # -------------------------------------------------
    if re.match(r"^CALL\b", command, re.IGNORECASE):

        program_name = get_parameter(command, "PGM")

        if not program_name:
            print("Required parameter PGM missing.")
        else:
            print(execute_program(program_name))

        return True

    # EXIT

    if upper in ("EXIT", "QUIT", "BYE"):
        return False

    if upper in ("HELP", "HELP *"):
        print("""
Available commands:

  CRTLIB LIB(name)
  WRKLIB
  WRKLIB name
  DSPLIB LIB(name)

  CRTPF FILE(lib/file) FIELDS(field:type,...)
  CRTLF FILE(lib/file) BASE(lib/file) ORDERBY(field,...)
  DSPFD FILE(lib/file)
  DSPFFD FILE(lib/file)

  CALL PGM(lib/program)
                            
  HELP
  EXIT
""")
        return True

    print("Command not recognized.")
    print("Type HELP for available commands.")

    return True

def execute_program(program_reference):
    """
    Execute a compiled COBOL program.

    Example:
        GANADERIA/HELLO
    """

    parts = program_reference.upper().split("/")

    if len(parts) != 2:
        return "Invalid program reference. Use LIBRARY/PROGRAM."

    library, program = parts

    if not re.fullmatch(r"[A-Z0-9_]{1,10}", library):
        return "Invalid library name."

    if not re.fullmatch(r"[A-Z0-9_]{1,10}", program):
        return "Invalid program name."

    base_dir = Path(__file__).resolve().parents[2]

    executable = base_dir / "cobol" / "bin" / program.lower()

    if not executable.is_file():
        return f"Program {library}/{program} not found. Compile it first."

    try:
        result = subprocess.run(
            [str(executable)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(base_dir)
        )

        output = result.stdout or ""

        if result.stderr:
            output += "\nERROR OUTPUT:\n" + result.stderr

        if result.returncode != 0:
            output += f"\nProgram ended with return code {result.returncode}."

        return output.strip() or "Program executed successfully."

    except subprocess.TimeoutExpired:
        return "Program execution timeout."

    except Exception as error:
        return f"Program execution error: {error}"