import secrets
import base64
import os

def generate_secret_key():
    """Generate a secure random key suitable for JWT signing"""
    return base64.b64encode(secrets.token_bytes(32)).decode('utf-8')

if __name__ == "__main__":
    key = generate_secret_key()
    print(f"Generated SECRET_KEY: {key}")
    
    # Check if .env file exists
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_contents = f.read()
        
        # Check if SECRET_KEY is already in .env
        if "SECRET_KEY=" in env_contents:
            print("\nYour .env file already contains a SECRET_KEY.")
            update = input("Do you want to replace it? (y/n): ").lower() == 'y'
            if update:
                # Replace existing SECRET_KEY
                with open(".env", "w") as f:
                    f.write(env_contents.replace(
                        # Match SECRET_KEY=any_value_until_newline
                        [line for line in env_contents.split('\n') if line.startswith("SECRET_KEY=")][0],
                        f"SECRET_KEY={key}"
                    ))
                print("SECRET_KEY updated in .env file.")
            else:
                print("SECRET_KEY not updated.")
        else:
            # Append SECRET_KEY to .env
            with open(".env", "a") as f:
                f.write(f"\n# Security\nSECRET_KEY={key}\n")
            print("SECRET_KEY added to .env file.")
    else:
        print("\nNo .env file found. Creating one with the SECRET_KEY.")
        with open(".env", "w") as f:
            f.write(f"# Security\nSECRET_KEY={key}\n")
        print(".env file created with SECRET_KEY.")