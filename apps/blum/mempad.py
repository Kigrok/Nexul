from apps.blum.data import BlumData
from core.web import Web
from core.cache import Cache
from asyncio import sleep as asleep, gather as agather
from random import uniform, randint, sample, shuffle

class BlumMempad:
    """
    BlumMempad is a utility class designed to interact with a mempad service through various asynchronous operations.
    The class uses caching, web requests, and data from BlumData to fetch or manipulate mempad data.

    Attributes:
        name (``str``): The name of the session or instance.
        web (``Web``): A Web instance for performing HTTP operations.
        cache (``Cache``): A Cache instance for caching values.
        urls (``dict[str, str]``): A dictionary of URLs mapped to method names, sourced from BlumData.
    """
    __slots__ = ['name', 'web', 'cache', 'urls']

    def __init__(self, name: str, web: Web, cache: Cache):
        """
        Initializes the BlumMempad instance with session name, web client, and cache client.

        Args:
            name (``str``): The name of the session or instance.
            web (``Web``): Web client for performing HTTP requests.
            cache (``Cache``): Cache client for storing temporary data.
        """
        self.name: str = name
        self.web: Web = web
        self.cache: Cache = cache
        self.urls: dict[str, str] = BlumData.mempad

    async def partner(self) -> dict:
        """
        Fetches the partner data from the mempad API.

        Returns:
            ``dict``: The partner data retrieved from the API.
        """
        url: str = self.partner.__name__
        return await self.web.get_data(url=self.urls[url])

    async def created_at(self) -> dict:
        """
        Fetches the creation date data from the mempad API.

        Returns:
            ``dict``: The creation date data retrieved from the API.
        """
        url: str = self.created_at.__name__
        return await self.web.get_data(url=self.urls[url])

    async def spotlight(self) -> dict:
        """
        Fetches spotlight data from the mempad API.

        Returns:
            ``dict``: The spotlight data retrieved from the API.
        """
        url: str = self.spotlight.__name__
        return await self.web.get_data(url=self.urls[url])

    async def live(self) -> dict:
        """
        Fetches live data from the mempad API.

        Returns:
            ``dict``: The live data retrieved from the API.
        """
        url: str = self.live.__name__
        return await self.web.get_data(url=self.urls[url])
    
    async def rate(self) -> dict:
        """
        Posts rate data to the mempad API if the currency ID is present in the cache.

        Returns:
            ``dict``: The response data from the API, or None if currency ID is not in the cache.
        """
        url: str = self.rate.__name__
        if await self.cache.__contains__('currencyId') == True:
            json: dict = {'amount': 1,'currency': {'from': await self.cache.get('currencyId')}}
            return await self.web.post_data(url=self.urls[url], data=json)
        
    async def transactions(self) -> dict:
        """
        Fetches transaction data from the mempad API.

        Returns:
            ``dict``: The transaction data retrieved from the API.
        """
        url: str = self.transactions.__name__
        return await self.web.get_data(url=self.urls[url])
    
    async def nearest_to_listing(self) -> dict:
        """
        Fetches the nearest-to-listing data from the mempad API.

        Returns:
            ``dict``: The nearest-to-listing data retrieved from the API.
        """
        url: str = self.nearest_to_listing.__name__
        return await self.web.get_data(url=self.urls[url])
    
    async def published_at(self) -> dict:
        """
        Fetches publication date data from the mempad API.

        Returns:
            ``dict``: The publication date data retrieved from the API.
        """
        url: str = self.published_at.__name__
        return await self.web.get_data(url=self.urls[url])
    
    async def market_cap(self) -> dict:
        """
        Fetches market capitalization data from the mempad API.

        Returns:
            ``dict``: The market cap data retrieved from the API.
        """
        url: str = self.market_cap.__name__
        return await self.web.get_data(url=self.urls[url])
    
    async def _position(self) -> str:
        """
        Constructs the URL for fetching position data based on the cached address.

        Returns:
            ``str``: The complete URL for the position data.
        """
        return f'{self.urls.get('positions')}{await self.cache.get('address')}'
    
    async def positions(self) -> dict:
        """
        Fetches position data from the mempad API if the address is present in the cache.
        
        Returns:
            ``dict``: The position data retrieved from the API, or None if address is not in the cache.
        """
        if await self.cache.__contains__('address') == True:
            url: str = await self._position()
            return await self.web.get_data(url=url)
        
    async def _random_mem(self) -> None:
        """
        Randomly selects and executes a subset of predefined asynchronous methods 
        related to mempad data. The order of execution is shuffled.
        """
        methods: list = [
            self.transactions, self.nearest_to_listing, 
            self.published_at, self.market_cap, self.positions]
        num_methods: int = randint(1, len(methods))
        selected_methods: list = sample(methods, num_methods)
        shuffle(selected_methods)
        for method in selected_methods:
            await method()

    async def mempad(self) -> None:
        """
        Executes a series of asynchronous operations including fetching partner, creation date,
        spotlight, and live data, followed by posting rate data and invoking a random function.
        """
        await agather(
            self.partner(),
            self.created_at(),
            self.spotlight(),
            self.live())
        await self.rate()
        await asleep(uniform(1, 5))
        await self._random_mem()