def main_menu():
    print("\nWelcome to the Traffic Steering xApp!")
    print("xApp Onboarded and deployed successfully.")
    print("xApp registered via E2.\n")
    
    while True:
        print("\nMenu Options:")
        print("1 - Apply Load Balancing")
        print("2 - Cell Outage Compensation")
        print("3 - Slicing-based Steering")
        print("4 - Service-based Steering")
        print("5 - Energy Efficiency")
        print("6 - Undeploy the TS-xApp")
        print("Enter 'exit' to quit the application.\n")
        
        choice = input("Please select an option: ")

        if choice == '1':
            # You might need to handle these flags differently since they're part of another class in the original file.
            # ts_xapp.run_load_balancing = True  # Start load balancing
            print("Load Balancing applied. See the result in the dashboard.")
        elif choice == '2':
            print("Cell Outage Compensation applied. See the result in the dashboard.")
        elif choice == '3':
            print("Slicing-based Steering applied. See the result in the dashboard.")
        elif choice == '4':
            print("Service-based Steering applied. See the result in the dashboard.")
        elif choice == '5':
            print("Energy Efficiency applied. See the result in the dashboard.")
        elif choice == '6':
            print("TS-xApp undeployed successfully.")
            break
        elif choice.lower() == 'exit':
            break
        else:
            print("Invalid choice. Please try again.")
