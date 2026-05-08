class Token:
    def __init__(self, username: str, access_token: str):
        if not access_token:
            raise ValueError('Access token is empty')
        self.__username = username
        self.__access_token = access_token

    @property
    def username(self) -> str:
        return self.__username

    @property
    def access_token(self) -> str:
        return self.__access_token
