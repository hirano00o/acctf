import pyotp

def get_code(totp: str) -> str:
    return pyotp.TOTP(totp).now()
