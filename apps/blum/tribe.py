from apps.blum.data import BlumData
from core.web import Web
from asyncio import sleep as asleep
from random import uniform

class BlumTribe:
    """
    BlumTribe is a class that provides methods for interacting with tribe-related services.
    It uses asynchronous operations to fetch data, perform actions like joining tribes, and retrieve leaderboard information.

    Attributes:
        name (``str``): The name of the session or instance.
        urls (``dict[str, str]``): A dictionary of URLs for tribe endpoints, sourced from BlumData.
        web (``Web``): An instance of the Web class for performing HTTP operations.
    """
    __slots__ = ('name', 'urls', 'web')

    def __init__(self, name: str, web: Web) -> None:
        """
        Initializes the BlumTribe instance with a session name and web client.

        Args:
            name (``str``): The name of the session or instance.
            web (``Web``): Web client for performing HTTP requests.
        """
        self.name: str = name
        self.urls: dict[str, str] = BlumData.tribe
        self.web: Web = web
        
    @property
    def my_tribe(self) -> str:
        """
        Returns the identifier of the current tribe.

        Returns:
            ``str``: The identifier of the current tribe from BlumData.
        """
        return BlumData.my_tribe
    
    async def join(self, idx: str) -> str:
        """
        Constructs the URL for joining a tribe based on the given index.

        Args:
            idx (``str``): The identifier of the tribe to join.

        Returns:
            ``str``: The URL for joining the tribe.
        """
        url: str = self.tribes.__name__
        return f'{self.urls[url]}{idx}/join'
        
    async def tribe_my(self) -> tuple[str, int, float]:
        """
        Fetches data about the current tribe.

        Returns:
            ``tuple[str, int, float]``: A tuple containing the title, number of members, and earned balance of the tribe.
        """
        url: str = self.tribe_my.__name__
        data: dict = await self.web.get_data(url=self.urls.get(url))
        title: str = data.get('title', '')
        members: int = data.get('countMembers', 0)
        balance: float = data.get('earnBalance', 0)
        return title, members, balance
            
    async def leaderboard(self) -> dict:
        """
        Fetches the leaderboard data for tribes.

        Returns:
            ``dict``: The leaderboard data retrieved from the API.
        """
        url: str = self.leaderboard.__name__
        return await self.web.get_data(url=self.urls[url])

    async def tribe_bot(self) -> dict:
        """
        Fetches data about the tribe bot.

        Returns:
            ``dict``: The tribe bot data retrieved from the API.
        """
        url: str = self.tribe_bot.__name__
        return await self.web.get_data(url=self.urls[url])

    async def tribes(self) -> dict:
        """
        Fetches data about all tribes.

        Returns:
            ``dict``: The data about all tribes retrieved from the API.
        """
        url: str = self.tribes.__name__
        return await self.web.get_data(url=self.urls[url])

    async def search_tribe(self) -> dict:
        """
        Searches for a tribe using the current tribe's identifier.

        Returns:
            ``dict``: The search result data retrieved from the API.
        """
        url: str = self.search_tribe.__name__
        return await self.web.get_data(url=f'{self.urls[url]}{self.my_tribe}')
        
    async def chatname(self) -> str:
        """
        Fetches the chat name associated with the current tribe.

        Returns:
            ``str``: The chat ID of the current tribe.
        """
        url: str = self.chatname.__name__
        data: dict = await self.web.get_data(url=f'{self.urls[url]}{self.my_tribe}')
        idx: str = data.get('id', '')
        return idx

    async def _join_tribe(self, idx: str) -> dict:
        """
        Sends a request to join a tribe based on the given index.

        Args:
            idx (``str``): The identifier of the tribe to join.

        Returns:
            ``dict``: The response data from the join request.
        """
        url = await self.join(idx=idx)
        return await self.web.post_data(url=url, data=None)

    async def join_tribe(self) -> None:
        """
        Executes a sequence of asynchronous operations to join a tribe.
        This includes fetching tribe bot data, retrieving tribes, searching for a tribe,
        fetching chat information, and sending a join request.
        """
        await self.tribe_bot()
        await asleep(uniform(1, 3))
        await self.tribes()
        await self.search_tribe()
        await asleep(0.2)
        idx: str = await self.chatname()
        await self.tribe_my()
        await self._join_tribe(idx=idx)
        await asleep(1)
        await self.tribe_my()