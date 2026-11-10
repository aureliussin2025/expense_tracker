from pwdlib import PasswordHash

# this creates the password hashing object
# recommended is the argon2id? since thats the one i downloaded
password_hasher = PasswordHash.recommended()

#this is the hashing function, to hash the password
def hash_password(password: str) -> str:
    return password_hasher.hash(password)

# this is to verify the password
# the lib extracts the salt from teh stored hash
# returns true or fals depending whether the password/hashing is correct
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hasher.verify(
        plain_password,
        hashed_password
    )
