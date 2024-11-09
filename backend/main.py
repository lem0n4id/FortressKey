from password_manager import PasswordManager

def main():
    password_manager = PasswordManager()

    while True:
        print("\n--- Blockchain Password Manager ---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            username = input("Enter username: ")
            password = input("Enter password: ")
            if password_manager.register_user(username, password):
                print("User registered successfully!")
            else:
                print("Username already exists. Please choose a different username.")

        elif choice == '2':
            username = input("Enter username: ")
            password = input("Enter password: ")
            session_id = password_manager.login_user(username, password)
            if session_id:
                print("Login successful!")
                logged_in_menu(password_manager, session_id)
            else:
                print("Invalid username or password.")

        elif choice == '3':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

def logged_in_menu(password_manager, session_id):
    while True:
        print("\n--- Password Management ---")
        print("1. Add Password")
        print("2. Get All Passwords")
        print("3. Update Password")
        print("4. Delete Password")
        print("5. Print all transactions")
        print("6. Logout")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            website = input("Enter website: ")
            username = input("Enter username: ")
            password = input("Enter password: ")
            if password_manager.add_password(website, username, password):
                print("Password added successfully!")
            else:
                print("Failed to add password.")

        elif choice == '2':
            passwords = password_manager.get_all_passwords()
            if passwords:
                print("\nAll stored passwords:")
                for entry in passwords:
                    print(f"Website: {entry['website']}")
                    print(f"Username: {entry['username']}")
                    print(f"Password: {entry['password']}")
                    print("------------------------")
            else:
                print("No passwords found.")

        elif choice == '3':
            website = input("Enter website: ")
            username = input("Enter username: ")
            new_password = input("Enter new password: ")
            if password_manager.update_password(website, username, new_password):
                print("Password updated successfully!")
            else:
                print("Password not found.")

        elif choice == '4':
            website = input("Enter website to delete: ")
            username = input("Enter username to delete: ")
            if password_manager.delete_password(website, username):
                print("Password deleted successfully!")
            else:
                print("Password not found.")

        elif choice == '5':
            password_manager.print_all_transactions()

        elif choice == '6':
            password_manager.logout_user(session_id)
            print("Logged out successfully.")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
