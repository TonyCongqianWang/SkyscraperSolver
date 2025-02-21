import subprocess, sys

def execute_and_check_error(command):
    """
    Executes a command in the terminal and checks for "Error" in the output.

    Args:
        command: The command to execute as a string.
    """
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # Capture output as text
        )
        stdout, stderr = process.communicate()

        output = stdout + stderr #Combine standard output and standard error
        if "Error" in output:
            with open("tmp2.txt", "a") as f:
                f.write(command + "\n")
            print(f"Command '{command}' resulted in an error. Saved to tmp2.txt.")
        else:
            print(f"Command '{command}' executed successfully.")

    except FileNotFoundError: #Handle cases where the command does not exist
        print(f"Command '{command}' not found.")
    except Exception as e: # Catch other potential exceptions
        print(f"An error occurred while executing '{command}': {e}")

if __name__ == "__main__":
    for line in sys.stdin:
        command = line.strip()  # Remove leading/trailing whitespace, including newline
        if command: #handle empty lines
            execute_and_check_error(command)
