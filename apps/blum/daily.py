from apps.blum.data import BlumData
from core.web import Web
from core.utils import Utils
from logs import Logger

class BlumDaily:
    """
    A class to manage daily actions for the Blum application, including logging and claiming rewards.

    Attributes:
        name (``str``): The session name.
        web (``Web``): An instance of the Web client for API requests.
        logger (``Logger``): Logger for tracking operations.
    """
    __slots__ = ('name', 'web', 'logger')

    def __init__(self, name: str, web: Web) -> None:
        """
        Initialize the BlumDaily class with session name and web client.

        Args:
            name (``str``): The session name.
            web (``Web``): An instance of the Web client.
        """
        self.name: str = name
        self.web: Web = web
        self.logger: Logger = Logger(
            name=__class__.__name__,
            session=self.name)
        
    @property
    def url(self) -> str:
        """
        URL for the daily endpoint.
        
        Returns:
            ``str``: The URL for daily API requests.
        """
        return BlumData.daily

    async def daily(self) -> None:
        """
        Fetch and log the current status of the daily reward.

        Returns:
            ``str``: The claim status ('available', 'unavailable', etc.).
        """
        data: dict = await self.web.get_data(url=self.url)
        claim: str = str(data.get('claim', 'unavailable') or 'unavailable')
        canClaimAt: int = int(data.get('canClaimAt', 0) or 0)
        time: str = await Utils(name=self.name).convert_time(timestamp=canClaimAt)
        await self.logger.log_debug(
            f'Daily Claim at: {str(time)}')
        return claim

    async def _claim(self) -> None:
        """
        Claim the daily reward and log the result.

        This method sends a POST request to claim the daily reward and logs
        the reward details, including streak day, points, and passes.
        """
        data: dict = await self.web.post_data(url=self.url, data=None)
        claimed: bool = bool(data.get('claimed', False) or False)
        day: int = int(data.get('currentStreakDays', 0) or 0)
        points: int = int(data.get('claimedReward', {}).get('points', 0) or 0)
        passes: int = int(data.get('claimedReward', {}).get('passes', 0) or 0)
        if claimed == True:
            await self.daily()
            await self.logger.log_info(
                f'Daily Claim | Day: {int(day)} | Points: {int(points)} | Passes: {int(passes)}')

    async def daily_claim(self, claim: str) -> None:
        """
        Check if the daily claim is available and process it.

        Args:
            claim (``str``):  The claim status.

        If the claim status is 'available', it triggers the `_claim` method.
        """
        if claim == 'available':
            await self._claim()