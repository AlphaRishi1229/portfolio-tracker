"""Common elements to be used throught the project."""
import hashlib
import secrets


secret_key = "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZWQyNTUxOQAAACCQcN775SDLvNoGp+V80GxVFe5D22mEPotbfs5u7CGVGgAAAJg54EI7OeBCOwAAAAtzc2gtZWQyNTUxOQAAACCQcN775SDLvNoGp+V80GxVFe5D22mEPotbfs5u7CGVGgAAAEACNR2efACy2PGTbX3VUcdC07hIld5OIUo3ZNnvEexYcpBw3vvlIMu82gan5XzQbFUV7kPbaYQ+i1t+zm7sIZUaAAAAFXJpc2hpa2VzaHZnQGdtYWlsLmNvbQ=="  # noqa

def hash_generate(string, secret=secret_key):
    """Used to generated hash for the input.

    Arguments:
        string {[type]} -- The input which needs to be hashed.

    Keyword Arguments:
        secret {[type]} -- Key used to hash

    Returns:
        calculated_hash[hash] -- The hashed result
    """
    to_be_hashed = (string.replace(" ", "")) + secret
    calculated_hash = hashlib.sha256(to_be_hashed.encode("utf-8")).hexdigest()
    return calculated_hash


def authorised(
    received_username: str, received_password: str,
    db_username: str, db_password: str
):
    is_authorised: bool = True
    hashed_password = hash_generate(received_password)
    correct_username = secrets.compare_digest(received_username, db_username)
    correct_password = secrets.compare_digest(hashed_password, db_password)
    if not (correct_username and correct_password):
        is_authorised = False
    return is_authorised
