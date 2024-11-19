import bcrypt

# Number of rounds to use for hashing
rounds = 5

def hash_password(password: str) -> bytes:
    # Hash a password for the first time, with a randomly-generated salt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds))

def verify_password(password: str, hashed_password: bytes) -> bool:
    # Check hashed password. It should be the same as hashed
    return bcrypt.checkpw(password.encode(), hashed_password)