from typing import List
import requests
from ..database.connect import redis_client
from datetime import timedelta
from fastapi.responses import JSONResponse
from ..core.config import settings
from ..middleware.logging import logger
from fastapi import status
from redis.exceptions import RedisError
import pickle


def login_api(email: str, password: str) -> JSONResponse:
    """Login API to grant access to user

    :param email: email of the user
    :type email: str
    :param password: password of the user
    :type password: str
    :return: A json with log in success or an error message
    :rtype: JSONResponse
    """

    logger.info("%s - %s", email, "Login function execution starts")
    try:
        data = {
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "username": email,
            "password": password,
            "grant_type": "password",
        }

        response = requests.post(
            f"https://{settings.AUTH0_DOMAIN}/oauth/token", data=data
        )
        print(response.status_code)
        if response.status_code == 403:
            logger.error("%s - %s", email, "Wrong email or password")
            return JSONResponse(
                content={"message": "Wrong email or password"},
                status_code=status.HTTP_403_FORBIDDEN,
            )
        if response.status_code == 401:
            logger.error("%s - %s", email, "Invalid Client ID or Secret")
            return JSONResponse(
                content={"message": "Invalid Client ID or Secret"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        access_token = response.json()["access_token"]
        cache = {"email": email}
        try:
            redis_client.set(access_token, pickle.dumps(cache))
            redis_client.expire(access_token, timedelta(seconds=21600))
        except RedisError as err:
            print(err)
            logger.error("%s - %s", email, "Error while storing token to redis")
            return JSONResponse(
                content={"message": "Exception in redis"}, status_code=500
            )

        res2 = JSONResponse(content={"token": access_token}, status_code=200)
        res2.set_cookie("Authorization", f"Bearer {access_token}")
        logger.info("%s - %s", email, "Login function execution complete")
        return res2
    except Exception as e:
        print(e)
        logger.error("%s - %s", email, "Login API failed")
        return JSONResponse(content={"message": "Exception occurred"}, status_code=500)


def logout_api(auth: List) -> JSONResponse:
    """Logout API to remove access of user

    :param auth: List of Access token and Email
    :type auth: List
    :return: Logout success message
    :rtype: JSONResponse
    """
    logger.info("%s - %s", auth[1]["email"], "Logout function execution starts")
    try:
        response = JSONResponse(content={"message": "Logged out successfully"})
        redis_client.delete(auth[0])
        response.delete_cookie("Authorization")
        logger.info("%s - %s", auth[1]["email"], "Logout function execution complete")
        return response
    except RedisError:
        logger.error(
            "%s - %s", auth[1]["email"], "Error while deleting token from redis"
        )
        return JSONResponse(content={"message": "Exception in redis"}, status_code=500)
    except Exception:
        logger.error("%s - %s", auth[1]["email"], "Logout API failed")
        return JSONResponse(content={"message": "Exception occurred"}, status_code=500)
