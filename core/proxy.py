from core.files import Files
from core.types import ProxyType, WebProxy

class Proxy:
    """
    A class for managing proxy configurations related to a specific service (e.g., Telegram).

    The class fetches proxy settings for the service and formats them into a structure that can be used by
    the application for network requests.

    Attributes:
        __name (``str``): The name of the service or proxy configuration to be fetched.
    """
    __slots__ = ('__name')

    def __init__(self, name: str) -> None:
        """
        Initializes the Proxy instance with the service name.

        Args:
            name (``str``): The name of the service or configuration.
        """
        self.__name: str = name

    async def _get_proxy(self) -> ProxyType | None:
        """
        Fetches proxy configuration for the service using the service name.

        Returns:
            ``ProxyType1`` | ``None``: The proxy configuration, or None if not found.
        """
        return await Files().get_info(
            name=self.__name,
            filter=__class__.__name__.lower())

    async def _generate_proxy(self, proxy: ProxyType) -> WebProxy:
        """
        Generates a dictionary with proxy details formatted for web use (HTTP/HTTPS).

        Args:
            proxy (``ProxyType``): The proxy configuration to format.

        Returns:
            ``WebProxy``: A dictionary containing HTTP/HTTPS proxy settings.
        """
        sheme: str = proxy.get('scheme')
        username: str = proxy.get('username')
        password: str = proxy.get('password')
        host: str = proxy.get('hostname')
        port: int = proxy.get('port')
        proxy: str = f'{sheme}://{username}:{password}@{host}:{port}'
        return {'http': proxy, 'https': proxy}

    async def get_tg_proxy(self) -> ProxyType | None:
        """
        Fetches the proxy configuration specifically for Telegram.

        Returns:
            ``ProxyType`` | ``None``: The proxy configuration for Telegram, or None if not found.
        """
        return await self._get_proxy()

    async def get_web_proxy(self) -> WebProxy | None:
        """
        Fetches the web proxy configuration and generates the formatted proxy string.

        Returns:
            ``WebProxy`` | ``None``: A dictionary containing the HTTP/HTTPS proxy configuration, or None if not found.
        """
        proxy: ProxyType = await self._get_proxy()
        if proxy is not None:
            return await self._generate_proxy(proxy=proxy)