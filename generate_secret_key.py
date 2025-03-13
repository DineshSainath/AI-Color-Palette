import secrets

# Generate a secure random secret key
secret_key = secrets.token_hex(16)
print(f"Generated SECRET_KEY: {secret_key}")
print("\nAdd this to your .env file and Vercel environment variables.") 