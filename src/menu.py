import sys

# Function to print options in a formatted manner
def print_options(options):
    for key, value in options.items():
        print(f"\033[1;36m{key}\033[0m: \033[1m{value}\033[0m")  # Cyan for key, bold for description

def main_menu():
    # Clear the screen
    print("\033[H\033[J")  # This escape sequence clears the screen

    print("\033[1;33mWelcome to the Traffic Steering xApp!\033[0m\n")  # Yellow for the welcome message
    
    options = {
        "1": "Apply Load Balancing",
        "2": "Cell Outage Compensation",
        "3": "Slicing-based Steering",
        "4": "Service-based Steering",
        "5": "Energy Efficiency",
        "6": "Undeploy the TS-xApp",
        "exit": "Quit the application"
    }

    while True:
        print("\n\033[4mMenu Options:\033[0m")  # Underline for the section title
        print_options(options)
        print()  # Print a newline for better spacing

        choice = input("\033[1;34mPlease select an option:\033[0m ")  # Blue for the input prompt

        if choice == '1':
            print("\033[1;32mLoad Balancing applied. See the result in the dashboard.\033[0m")  # Green for success
        elif choice == '2':
            print("\033[1;32mCell Outage Compensation applied. See the result in the dashboard.\033[0m")
        elif choice == '3':
            print("\033[1;32mSlicing-based Steering applied. See the result in the dashboard.\033[0m")
        elif choice == '4':
            print("\033[1;32mService-based Steering applied. See the result in the dashboard.\033[0m")
        elif choice == '5':
            print("\033[1;32mEnergy Efficiency applied. See the result in the dashboard.\033[0m")
        elif choice == '6':
            print("\033[1;31mTS-xApp undeployed successfully.\033[0m")  # Red for important actions
            break
        elif choice.lower() == 'exit':
            break
        else:
            print("\033[1;31mInvalid choice. Please try again.\033[0m")  # Red for errors

# This part is only necessary if you want to run menu.py as a standalone script.
if __name__ == "__main__":
    main_menu()

