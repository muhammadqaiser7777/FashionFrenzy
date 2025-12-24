from middleware.encrypt import hash_password_admin

def generate_admin_password(password):
    """Generates a hashed password for admin using the admin-specific hash function."""
    return hash_password_admin(password)

if __name__ == "__main__":
    password = input("Enter password: ")
    hashed = generate_admin_password(password)
    print(f"Hashed password: {hashed}")