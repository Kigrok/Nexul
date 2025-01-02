from apps.blum.data import BlumData
from core.web import Web
from core.files import Files
from core.telegram import Telegram

class BlumLogin:
    """
    Handles user login and session management for the Blum application.

    This class encapsulates all the logic required to authenticate a user,
    manage session tokens, and refresh authentication data when necessary.
    It adheres to the Single Responsibility Principle by focusing exclusively
    on login and token-related operations.
    
    Attributes:
        name (``str``): The name or identifier of the user/session.
        web (``Web``): An instance of the Web class for managing HTTP requests.
        refresh_token (``str``): Holds the refresh token for session renewal.
    """
    __slots__ = ('name', 'web', 'refresh_token')

    def __init__(self, name: str) -> None:
        """
        Initializes the BlumLogin instance with a user name and related configurations.

        Args:
            name (``str``): The identifier for the user/session.
        """
        self.name: str = name
        self.web: Web = Web(name=self.name)

    @property
    def referralToken(self) -> str:
        """
        Returns the referral token required for authentication requests.

        Returns:
            ``str``: The referral token for the Blum application.
        """
        return BlumData.referralToken
    
    @property
    def app_url(self) -> str:
        """
        Returns the URL of the Blum application.

        Returns:
            ``str``: The URL of the Blum application.
        """
        return BlumData.app_url
    
    @property
    def app_name(self) -> str:
        """
        Returns the name of the Blum application.

        Returns:
            ``str``: The name of the Blum application.
        """
        return BlumData.app_name
    
    @property
    def auth_url(self) -> str:
        """
        Returns the URL of the authentication endpoint.

        Returns:
            ``str``: The URL of the authentication endpoint.
        """
        return BlumData.login['auth_url']
    
    @property
    def refresh_url(self) -> str:
        """
        Returns the URL of the refresh token endpoint.

        Returns:
            ``str``: The URL of the refresh token endpoint.
        """
        return BlumData.login['refresh']

    async def _get_headers(self) -> dict[str, str]:
        """
        Prepares the HTTP headers required for authentication requests.
        Fetches user-specific headers, including the User-Agent, from a stored configuration file.

        Returns:
            ``dict[str, str]``: A dictionary of HTTP headers.
        """
        user_agent: str = await Files().get_info(name=self.name, filter='user_agent')
        return {
            **self.web.scraper.headers,
            'Accept': 'application/json, text/plain, */*',
            'Cache-Control': 'no-cache',
            'Origin': self.app_url,
            'Pragma': 'no-cache',
            'Priority': 'u=1, i',
            'User-Agent': user_agent}

    async def _get_data(self) -> dict[str, str]:
        """
        Fetches the necessary data for the login request.
        Retrieves application-specific data from the Telegram service.

        Returns:
            ``dict[str, str]``: A dictionary containing the query and referral token.
        """
        data: str = await Telegram(name=self.name).get_app_data(app=self.app_name)
        if self.name != 'kplaya':
            return {'query': data, 'referralToken': self.referralToken}
        else:
            return {'query': data}
    
    async def _login_token(self, data: dict[str, str]) -> tuple[str, str]:
        """
        Extracts the access and refresh tokens from the authentication response.

        Args:
            data (``diczt[str, str]``): The response data containing tokens.

        Returns:
            tuple[str, str]: The access and refresh tokens as a tuple.
        """
        access: str = data.get('token', {}).get('access', None)
        refresh: str = data.get('token', {}).get('refresh', None)
        return access, refresh

    async def _save_tokens(self, data: dict) -> None:
        """
        Saves the tokens from the authentication response and updates the HTTP headers.

        Args:
            data (``dict``): The response data containing tokens.

        Raises:
            ValueError: If either the access or refresh token is missing.
        """
        access, refresh = await self._login_token(data=data)
        if access is not None and refresh is not None:
            self.web.headers['Authorization'] = 'Bearer ' + access
            self.refresh_token: str = refresh
        
    async def login(self) -> None:
        """
        Performs the login operation by sending user credentials and saving tokens.

        This method combines fetching data, sending an HTTP POST request to the authentication
        endpoint, and saving the returned access and refresh tokens.
        """
        await self._save_tokens(
            data=await self.web.post_data(
                url=self.auth_url,
                data=await self._get_data()))
        
    async def refresh(self) -> None:
        """
        Refreshes the session by sending the refresh token to the appropriate endpoint.
        This ensures that the user remains authenticated without requiring a full login.
        """
        await self.web.post_data(
            url=self.refresh_url,
            data={'refresh': self.refresh_token})
        
    async def get_web(self) -> Web:
        """
        Configures the Web instance for authenticated requests.
        This method prepares HTTP headers, performs login, and refreshes the session
        to ensure that all subsequent requests are authenticated.

        Returns:
            ``Web``: An instance of the Web class configured with authentication headers.
        """
        self.web.headers = await self._get_headers()
        await self.login()
        await self.refresh()
        return self.web
