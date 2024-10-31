import bcrypt

salt = b'$2b$12$wE.fRv4cUoMjU45RIn2iD.'

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')