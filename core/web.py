from cloudscraper import CloudScraper, create_scraper
from core.types import WebProxy
from core.proxy import Proxy
from certifi import where

class Web:
    """
    A class that handles HTTP requests and web scraping using the CloudScraper library.

    This class provides methods to send GET, POST, and PUT requests, handle proxies, 
    and parse the responses, including downloading images.

    Attributes:
        __name (``str``): The name of the session, typically used for logging or configuration.
        scraper (``CloudScraper``): The instance of CloudScraper for making HTTP requests.
        headers (``dict``): The default headers used for requests made by the scraper.
        __proxy (``WebProxy`` | ``None``): The proxy configuration, if any, used for web requests.
    """
    __slots__ = ('__name', 'scraper', 'headers', '__proxy')

    def __init__(self, name: str) -> None:
        """
        Initializes the Web class with the provided session name and creates a CloudScraper instance.

        Args:
            name (``str``): The name of the session used for logging and configuration.
        """
        self.__name: str = name
        self.scraper: CloudScraper = create_scraper()
        self.headers: dict = self.scraper.headers

    async def _get_proxy(self) -> None:
        """
        Retrieves the proxy settings for the web requests.

        This method fetches the proxy configuration based on the session name and stores it in the 
        `__proxy` attribute.

        The proxy is used to route requests through a specified network, if configured.
        """
        self.__proxy: WebProxy | None = await Proxy(name=self.__name).get_web_proxy()

    async def _get_request(self, url: str) -> CloudScraper:
        """
        Sends an asynchronous GET request to the specified URL.

        Args:
            url (``str``): The URL to send the GET request to.

        Returns:
            ``CloudScraper``: The response object containing the data from the GET request.
        """
        await self._get_proxy()
        response: CloudScraper = self.scraper.get(
            url=url, 
            headers=self.headers,
            verify=where(),
            proxies=self.__proxy,
            timeout=30)
        return response
    
    async def _post_request(self, url: str, data: dict | None = None) -> CloudScraper:
        """
        Sends an asynchronous POST request to the specified URL with optional data.

        Args:
            url (``str``): The URL to send the POST request to.
            data (``dict | None``): Optional data to include in the POST request.

        Returns:
            ``CloudScraper``: The response object containing the data from the POST request.
        """
        await self._get_proxy()
        response: CloudScraper = self.scraper.post(
            url=url, 
            headers=self.headers,
            json=data, 
            verify=where(),
            proxies=self.__proxy)
        return response
    
    async def _put_request(self, url: str, data: dict | None = None) -> CloudScraper:
        """
        Sends an asynchronous PUT request to the specified URL with optional data.

        Args:
            url (``str``): The URL to send the PUT request to.
            data (``dict | None``): Optional data to include in the PUT request.

        Returns:
            ``CloudScraper``: The response object containing the data from the PUT request.
        """
        await self._get_proxy()
        response: CloudScraper = self.scraper.put(
            url=url,
            headers=self.headers,
            json=data,
            verify=where(),
            proxies=self.__proxy,
            timeout=30)
        return response
    
    async def _content_type(self, response: CloudScraper) -> dict | str:
        """
        Parses the response based on its content type.

        This method checks the `Content-Type` header of the response and processes the response accordingly.

        Args:
            response (``CloudScraper``): The response object from a request.

        Returns:
            ``dict | str``: The parsed content, either as a JSON object or a plain text string.
        """
        if 'application/json' in response.headers.get('Content-Type', ''):
            return response.json()
        else: return response.text

    async def get_data(self, url: str) -> dict:
        """
        Retrieves data from a specified URL via a GET request.

        This method sends a GET request and processes the response, returning it as a parsed JSON object
        or text, depending on the content type.

        Args:
            url (``str``): The URL to retrieve data from.

        Returns:
            ``dict``: The parsed response, typically a dictionary if the response is JSON.
        """
        response: CloudScraper = await self._get_request(url=url)
        return await self._content_type(response=response)
    
    async def post_data(self, url: str, data: dict | None = None) -> dict:
        """
        Sends data to a specified URL via a POST request.

        This method sends a POST request with optional data and processes the response, returning it
        as a parsed JSON object or text, depending on the content type.

        Args:
            url (``str``): The URL to send data to.
            data (``dict | None``): Optional data to send with the POST request.

        Returns:
            ``dict``: The parsed response, typically a dictionary if the response is JSON.
        """
        response: CloudScraper = await self._post_request(url=url, data=data)
        return await self._content_type(response=response)
    
    async def download_image(self, url: str) -> bytes:
        """
        Downloads an image from the specified URL.

        This method sends a GET request to retrieve an image file and returns the raw binary content of
        the image.

        Args:
            url (``str``): The URL of the image to download.

        Returns:
            ``bytes``: The raw binary content of the image.
        """
        response: CloudScraper = await self._get_request(url)
        return response.content