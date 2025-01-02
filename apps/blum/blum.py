from apps.blum.data import BlumData
from apps.blum.daily import BlumDaily
from apps.blum.login import BlumLogin
from apps.blum.mempad import BlumMempad
from apps.blum.tribe import BlumTribe
from apps.blum.frens import BlumFrens
from apps.blum.wallet import BlumWallet
from apps.blum.game import BlumGame
from apps.blum.tasks import BlumTasks
from core.web import Web
from core.cache import Cache
from core.utils import Utils
from logs import Logger
from asyncio import sleep as asleep, gather as agather
from random import uniform, randint, sample, shuffle

class Blum:
    """
    The Blum class encapsulates the core functionality of the Blum application.
    It manages user sessions, handles various actions such as daily tasks, 
    wallet interactions, tribe joining, and random actions. Dependencies are 
    initialized dynamically during runtime.
    
    Attributes:
        name (``str``): The session name for the Blum instance.
        logger (``Logger``): Logger instance for tracking actions and errors.
        cache (``Cache``): Cache instance for storing temporary data.
        web (``Web``): Web instance for managing HTTP requests.
        tribe (``BlumTribe``): Handles tribe-related actions.
        daily (``BlumDaily``): Manages daily actions and rewards.
        frens (``BlumFrens``): Handles friend-related functionalities.
        wallet (``BlumWallet``): Manages wallet actions and balances.
        game (``BlumGame``): Handles game-related operations.
        tasks (``BlumTasks``): Manages tasks and their execution.
    """
    __slots__ = ('name', 'logger', 'cache', 'web', 'tribe', 'daily', 'frens', 'wallet', 'game', 'tasks')

    def __init__(self, name: str) -> None:
        """
        Initializes the Blum class with a session name, logger, and cache.

        Args:
            name (``str``): The name of the session.
        """
        self.name: str = name
        self.logger: Logger = Logger(
            name=__class__.__name__,
            session=self.name)
        self.cache: Cache = Cache()

    @property
    def _me(self) -> str:
        """
        Property to retrieve the endpoint URL for the user's profile.

        Returns:
            ``str``: The URL for accessing the user's profile.
        """
        return BlumData.me

    async def me(self) -> None:
        """
        Fetches and logs the user's profile information, such as username and ID.
        """
        data: dict = await self.web.get_data(url=self._me)
        username: str = data.get('username', None)
        idx: str = data.get('id', None).get('id', None)
        await self.logger.log_debug(
            f'Username: {str(username)} | ID: {str(idx)}')
        
    async def earn(self) -> None:
        """
        Retrieves tasks, waits for a short duration, and performs a set of actions
        including task processing, game balance check, and wallet checks.
        """
        tasks: list = await self.tasks.tasks()
        await asleep(6)
        await agather(
            self.game.balance(),
            self.wallet.points_balance(),
            self.wallet.usd())
        await self.tasks.work_task(tasks)
        
    async def mempad(self) -> None:
        """
        Executes the mempad-related functionality.
        """
        await BlumMempad(
            name=self.name,
            web=self.web,
            cache=self.cache).mempad()

    async def join_tribe(self, title: str) -> None:
        """
        Joins a tribe if no title is provided and then returns to the home actions.

        Args:
            title (``str``): The name of the tribe to join.
        """
        if title is None:
            await self.tribe.join_tribe()
            await self.home()
            
    async def daily_claim(self, claim: str) -> None:
        """
        Claims the daily reward and waits for a short duration.

        Args:
            claim (``str``): The claim token for the daily reward.
        """
        await self.daily.daily_claim(claim=claim)
        await asleep(uniform(1, 3))

    async def frends(self) -> None:
        """
        Executes friend-related actions, updates game balance, and waits briefly.
        """
        await self.frens.frens()
        await self.game.balance()
        await asleep(uniform(2, 5))
            
    async def home(self) -> None:
        """
        Performs a sequence of actions for the home screen, including claiming rewards,
        checking balances, and farming in the game.
        """
        await self.frens.friends_balance()
        claim: str = await self.daily.daily()
        title, _, __ = await self.tribe.tribe_my()
        await self.tribe.leaderboard()
        await asleep(uniform(2, 5))
        await self.join_tribe(title=title)
        await asleep(uniform(2, 5))
        await self.daily_claim(claim=claim)
        await asleep(uniform(2, 5))
        await self.game.farm()
        await asleep(uniform(2, 5))
    
    async def wallet_action(self) -> None:
        """
        Performs wallet-related actions, including checking balances and transaction history.
        """
        await agather(
            self.wallet.usd(),
            self.wallet.points_balance(),
            self.game.balance())
        await asleep(uniform(2, 5))
        await self.wallet.history()

    async def login(self) -> None:
        """
        Logs in the user and performs initial data retrieval actions.
        """
        await self.me()
        await asleep(0.1)
        await agather(
            self.game.now(),
            self.frens.friends_balance(),
            self.wallet.wallet_my(),
            self.frens.friends_balance(),
            self.tribe.tribe_my(),
            self.game.balance(),
            self.daily.daily(),
            self.wallet.usd())
        
    async def random_func(self) -> None: 
        """
        Randomly selects and executes a set of methods from the available options.
        """
        methods: list = [self.frends, self.mempad, self.earn, self.wallet_action]
        num_methods: int = randint(1, len(methods))
        selected_methods: list = sample(methods, num_methods)
        shuffle(selected_methods)
        for method in selected_methods:
            await method()
        
    async def blum(self) -> None:
        """
        Initializes dependencies, logs in the user, and performs the main sequence of actions.
        """
        self.web: Web = await BlumLogin(name=self.name).get_web()
        self.tribe: BlumTribe = BlumTribe(
            name=self.name,
            web=self.web)
        self.daily: BlumDaily = BlumDaily(
            name=self.name, 
            web=self.web)
        self.frens: BlumFrens = BlumFrens(
            name=self.name,
            web=self.web)
        self.wallet: BlumWallet = BlumWallet(
            name=self.name,
            web=self.web,
            cache=self.cache)
        self.game: BlumGame = BlumGame(
            name=self.name,
            web=self.web)
        self.tasks:BlumTasks = BlumTasks(
            name=self.name,
            web=self.web)
        await self.login()
        await self.home()
        await self.random_func()

    async def main(self) -> None:
        """
        Logs the start of the process, sleeps for a randomized duration, and initiates Blum actions.
        """
        await self.logger.log_info('Blum Start')
        await Utils(name=self.name)._sleep(min_sleep=80, max_sleep=240)
        await self.blum()
        await self.cache.clear()
