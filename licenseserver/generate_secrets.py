import secrets
import base64

# Generate random secrets
secret_key = secrets.token_urlsafe(32)
jwt_secret = secrets.token_urlsafe(32)
signing_secret = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')

# Write to .env file
with open('.env', 'w') as f:
    f.write(f'SECRET_KEY={secret_key}\n')
    f.write(f'JWT_SECRET={jwt_secret}\n')
    f.write(f'SIGNING_SECRET={signing_secret}\n')

print("[✔] Secrets generated and saved to .env")
