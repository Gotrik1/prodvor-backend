# reset_password.py
import os
from app import create_app, db
from app.models import User

# --- Credentials to set ---
EMAIL = "gotrik.smith@gmail.com"
PASSWORD = "12345678"
NICKNAME = "gotrik.smith" # Used only if the user does not exist
# ---

print("Starting password reset script...")
app = create_app()

with app.app_context():
    user = User.query.filter_by(email=EMAIL).first()

    if user:
        print(f"Found existing user with email '{EMAIL}'.")
        print("Resetting password...")
        user.set_password(PASSWORD)
        db.session.commit()
        print("Password has been successfully reset.")
    else:
        print(f"No user found with email '{EMAIL}'.")
        # Check if nickname is already taken before creating a new user
        nickname_user = User.query.filter_by(nickname=NICKNAME).first()
        if nickname_user:
            print(f"Error: Nickname '{NICKNAME}' is already taken. Cannot create new user.")
            print("Please edit reset_password.py with a different nickname and run again.")
        else:
            print("Creating a new user...")
            new_user = User(
                email=EMAIL,
                nickname=NICKNAME,
                role='player' # Default role
            )
            new_user.set_password(PASSWORD)
            db.session.add(new_user)
            db.session.commit()
            print(f"Successfully created new user '{NICKNAME}' with email '{EMAIL}'.")

print("\nScript finished. You can now try logging in with the credentials.")
