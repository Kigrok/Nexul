from apps.blum.data import BlumData
from core.web import Web
from core.utils import Utils
from logs import Logger
from asyncio import sleep as asleep
from random import uniform

class BlumFrens:
    """
    Class to manage operations related to friends (frens) in the Blum application.

    Attributes:
        name (``str``): The session name.
        web (``Web``): The Web client for making API requests.
        urls (``dict[str, str]``): Mapping of API endpoints for friends functionality.
        logger (``Logger``): Logger for tracking and debugging operations.
    """
    __slots__ = ['name', 'web', 'urls', 'logger']

    def __init__(self, name: str, web: Web) -> None:
        """
        Initialize the BlumFrens class.

        Args:
            name (``str``): The session name.
            web (``Web``): The Web client for API requests.
        """
        self.name: str = name
        self.web: Web = web
        self.urls: dict[str, str] = BlumData.frens
        self.logger: Logger = Logger(
            name=__class__.__name__,
            session=self.name)
        
    async def _friends_balance(self, data: dict) -> tuple[float, bool, int, int]:
        """
        Extract balance data from the API response.

        Args:
            data (dict): The response data from the API.

        Returns:
            ``tuple[float, bool, int, int]``: A tuple containing:
            - balance (``float``): The claimable amount.
            - canClaim (``bool``): Whether claiming is possible.
            - friends (``int``): Number of invited friends.
            - time (``int``): Time when claiming becomes available.
        """
        balance: float = float(data.get('amountForClaim', 0) or 0)
        canClaim: bool = bool(data.get('canClaim', False) or False)
        friends: int = int(data.get('usedInvitation', 0) or 0)
        time: int = int(data.get('canClaimAt', 0) or 0)
        return float(balance), bool(canClaim), int(friends), int(time)
    
    async def friends_balance(self) -> tuple[float, bool, int, int]:
        """
        Fetch and process friends' balance data.

        Returns:
            ``tuple[float, bool, int, int]``: Processed balance data.
        """
        url: str = self.friends_balance.__name__
        data: dict = await self.web.get_data(url=self.urls[url])
        return await self._friends_balance(data)
    
    async def friends_page(self) -> None:
        """
        Fetch and log details of the friends page.
        """
        url: str = self.friends_page.__name__
        data: dict = await self.web.get_data(url=self.urls[url])
        friends: list = list(data.get('friends', []) or [])
        await self.logger.log_debug(
            f'Friends: {int(len(friends))}')
        
    async def friends_claim(self) -> None:
        """
        Claim points for friends and log the balance after claiming.
        """
        url: str = self.friends_claim.__name__
        data: dict = await self.web.post_data(url=self.urls[url], data=None)
        balance: float = float(data.get('claimBalance', 0) or 0)
        await self.logger.log_info(
            f'Claim Friends Points: {float(balance):.4f}')
        
    async def friends_trading(self) -> dict:
        """
        Fetches trading-related data for friends.

        Returns:
            ``dict``: The data retrieved from the friends trading API.
        """
        url: str = self.friends_claim.__name__
        return await self.web.get_data(url=self.urls[url])
        
    async def frens(self) -> None:
        """
        Orchestrates the management of friends' related actions including:
        - Fetching balance data.
        - Logging the friends page.
        - Claiming points if eligible.
        - Handling claim timing and logging the details.
        """
        balance, canClaim, friends, time = await self.friends_balance()
        await self.friends_trading()
        await self.friends_page()
        await asleep(uniform(1, 5))
        if canClaim == True:
            await self.friends_claim()
            await self.friends_balance()
        else:
            if int(time) > 0:
                time: str = await Utils(name=self.name).convert_time(timestamp=time)
                await self.logger.log_info(
                    f'Friends: {int(friends)} | Balance: {float(balance):.4f} | Claim at: {str(time)}')
        await asleep(1.6)
        await self.friends_balance()
