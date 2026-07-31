from fastapi import Response

# For localhost
# def set_secure_cookie(response: Response, token: str):
#     response.set_cookie(
#         "prep_token",
#         token,
#         httponly=True,
#         max_age=1 * 24 * 60 * 60,  # 1 days
#     )
#     return response


# For deployment
def set_secure_cookie(response: Response, token: str):
    response.set_cookie(
        "prep_token",
        token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=1 * 24 * 60 * 60,  # 1 days
    )
    return response