from apps.blum.data import BlumData
from logs import Logger
from core.web import Web
from core.utils import Utils
from logging import DEBUG, INFO

class BlumGame:
    """
    A class to manage game-related actions for the Blum application, 
    including balance checking, farming operations, and logging.
    
    Attributes:
        name (``str``): The session name.
        web (``Web``): The Web client for API requests.
        logger (``Logger``): Logger for tracking operations.
        urls (``dict[str, str]``): URLs for game-related endpoints.
        farming (``int``): Timestamp indicating the end of the current farming session.
    """
    __slots__ = ('name', 'web', 'logger', 'urls', 'farming')

    def __init__(self, name: str, web: Web) -> None:
        """
        Initialize the BlumGame class with session name and web client.

        Args:
            name (``str``): The session name.
            web (``Web``): An instance of the Web client.
        """
        self.name: str = name
        self.web: Web = web
        self.urls: dict[str, str] = BlumData.game
        self.logger: Logger = Logger(
            name=__class__.__name__,
            session=self.name)
        
    async def now(self) -> int:
        """
        Get the current server timestamp.

        Returns:
            ``int``: The current timestamp from the server.
        """
        url: str = self.now.__name__
        data: dict = await self.web.get_data(url=self.urls[url])
        now: int = int(data.get('now', 1) or 1)
        return int(now)
    
    async def balance(self) -> None:
        """
        Fetch the current balance and play passes from the game API.
        Logs the balance and passes information.
        """
        url: str = self.balance.__name__
        data: dict = await self.web.get_data(url=self.urls[url])
        balance: float = float(data.get('availableBalance', 0) or 0)
        passes: int = int(data.get('playPasses', 0) or 0)
        self.farming: int = int(data.get('farming', {}).get('endTime', 1) or 1)
        await self.logger.log_info(
            f'Balance: {float(balance):.4f} | Passes: {int(passes)}')
        
    async def farm_claim(self) -> None:
        """
        Claim the rewards from farming.
        Logs the claim action.
        """
        url: str = self.farm_claim.__name__
        data: dict = await self.web.post_data(url=self.urls[url], data=None)
        balance: float = float(data.get('availableBalance', 0) or 0)
        passes: int = int(data.get('playPasses', 0) or 0)
        await self.logger.log_info(
            f'Claim Farm | Balance: {float(balance):.4f} | Passes: {int(passes)}')
        
    async def farm_start(self) -> None:
        """
        Start a new farming session.
        Logs the new farming end time.
        """
        url: str = self.farm_start.__name__
        data: dict = await self.web.post_data(url=self.urls[url], data=None)
        endTime: int = int(data.get('endTime', 0) or 0)
        time: str = await Utils(name=self.name).convert_time(timestamp=endTime)
        await self.logger.log_debug(
            f'New claim at: {str(time)}')
        
    async def farm(self) -> None:
        """
        Handle the farming lifecycle. Claims rewards if farming has ended 
        and starts a new farming session.
        """
        if int(self.farming) < int(await self.now()):
            await self.farm_claim()
            await self.farm_start()