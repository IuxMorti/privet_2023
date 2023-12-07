from fastapi import HTTPException


def check(verification_condition: bool, status_code, detail):
    if verification_condition:
        raise HTTPException(status_code=status_code,
                            detail=detail)
