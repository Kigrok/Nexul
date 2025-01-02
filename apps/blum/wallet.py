from apps.blum.data import BlumData
from logs import Logger
from core.web import Web
from core.cache import Cache
from logging import DEBUG, INFO
from json import JSONDecodeError

class BlumWallet:
    """
    A class to handle wallet-related operations for the Blum application.
    Includes fetching wallet details, USD balance, and points balance.
    
    Attributes:
        name (``str``): The session name.
        web (``Web``): The Web client for API requests.
        cache (``Cache``): A cache instance for temporary storage.
    """

    __slots__ = ['name', 'web', 'cache', 'urls', 'logger']

    def __init__(self, name: str, web: Web, cache: Cache) -> None:
        """
        Initialize the BlumWallet class with session name, web client, and cache.

        Args:
            name (``str``): The session name.
            web (``Web``): An instance of the Web client.
            cache (``Cache``): An instance of the Cache client.
        """
        self.name: str = name
        self.web: Web = web
        self.cache: Cache = cache
        self.urls: dict[str, str] = BlumData.wallet
        self.logger: Logger = Logger(
            name=__class__.__name__,
            session=self.name)
        
    async def wallet_my(self) -> float:
        """
        Fetch the wallet's address and store it in the cache.
        Logs the address if found.
        """
        url: str = self.wallet_my.__name__
        try:
            data: dict = await self.web.get_data(url=self.urls[url])
            address: str = data.get('address', None)
        except JSONDecodeError: raise
        finally:
            if address != None:
                await self.cache.set('address', address)
                await self.logger.log(
                    level=DEBUG,
                    message=f'Address: {str(address)}')
            
    async def usd(self) -> None:
        """
        Fetch the USD balance of the wallet if the address is cached.
        Logs the balance and currency details if available.
        """
        url: str = self.usd.__name__
        if await self.cache.__contains__('address') == True:
            data: dict = await self.web.get_data(url=self.urls[url])
            address: str = str(data.get('address', '') or '')
            usd: float = float(data.get('totalFiatValue', None).get('usd', 0) or 0)
            currencyId: str = str(data.get('tonBalance', {}).get('currencyId', None) or None)
            if currencyId is not None: await self.cache.set('currencyId', currencyId)
            await self.logger.log(
                level=INFO,
                message=f'Address: {str(address)} | USD: {float(usd):.2f}')
            
    async def points_balance(self) -> None:
        """
        Fetch the points balance in USD and log it.
        """
        url: str = self.points_balance.__name__
        data: dict = await self.web.get_data(url=self.urls[url])
        usd: float = float(data.get('totalFiatValue', None).get('usd', 0) or 0)
        await self.logger.log(
            level=INFO,
            message=f'Balance on USD: {float(usd):.2f}')
        
    async def history(self) -> dict:
        """
        Asynchronously retrieves the history data from the web.
        
        Returns:
            ``dict``: A dictionary containing the history data.
        """
        url: str = self.history.__name__
        return await self.web.get_data(url=self.urls[url])
    