from pyrogram import Client
from logs import Logger
from core.files import Files
from core.proxy import Proxy
from core.utils import Utils
from core.types import AccountConfig, ProxyType

class TGRegister:
    """
    A class that handles the registration of a new Telegram client session using provided session data.

    This class is responsible for:
    - Creating and managing a Telegram client using the Pyrogram library.
    - Setting up session details, device information, and proxy configurations.
    - Logging and handling errors during the registration process.

    Attributes:
        __name (``str``): The name of the session.
        logger (``Logger``): Logger instance for logging session events.
        client (``Client``): The Pyrogram client instance used for Telegram interactions.
    """
    __slots__ = ('__name', 'logger', 'client')

    def __init__(self, name: str) -> None:
        """
        Initializes the TGRegister instance with the session name.

        Args:
            name (``str``): The name of the session.
        """
        self.__name: str = name
        self.logger: Logger = Logger(
            name=__class__.__name__, 
            session=self.__name)
        
    @property
    def workdir(self) -> str:
        """
        Property that returns the working directory for session files.

        Returns:
            ``str``: The path to the session directory.
        """
        return Files().sessions_dir

    async def _clinet_log(self) -> None:
        """
        Logs the creation of the client.

        This is used for logging the process of client creation.
        """
        await self.logger.log_info(
            'Create client.')
        
    async def _session_log(self) -> None:
        """
        Logs the creation of the session.

        This is used to log when the session is created and ready.
        """
        await self.logger.log_info(
            f'Create session.')
        
    async def _erroe_log(self, error: str) -> None:
        """
        Logs an error that occurred during the process.

        Args:
            error (``str``): The error message to log.
        """
        await self.logger.log_error(
            f'An unexpected error occurred: {error}.')
        
    async def _get_session(self) -> AccountConfig:
        """
        Retrieves session data from files.

        Returns:
            ``AccountConfig``: The session configuration data.
        """
        return await Files().get_session_data(name=self.__name)
    
    async def add_device(self) -> None:
        """
        Adds device information if it's not already present.

        This method checks if the device model and user agent are already set in the session data.
        If not, it will use the `Utils` class to add the device details.
        """
        if await Files().get_info(name=self.__name, filter='device_model') == None \
            or await Files().get_info(name=self.__name, filter='user_agent') == None:
            await Utils(name=self.__name).add_device()

    async def _get_client(self) -> None:
        """
        Initializes the Telegram client with session details.

        This method retrieves session data and uses it to initialize a Pyrogram `Client` instance.
        It sets the necessary parameters like API ID, API hash, phone number, device model, etc.
        """
        await self._clinet_log()
        session: AccountConfig = await self._get_session()
        self.client: Client = Client(
            name=session.get('app_title'),
            api_id=session.get('api_id'),
            api_hash=session.get('api_hash'),
            phone_number=str(session.get('phone_number')),
            device_model=session.get('device_model'),
            workdir=self.workdir,
            password=str(session.get('password')))
        
    async def _get_proxy(self) -> None:
        """
        Retrieves and sets the proxy configuration for the client.

        If a proxy is configured for the session, it will be set up for the `Client` instance.
        """
        proxy: ProxyType = await Proxy(name=self.__name).get_tg_proxy()
        if proxy is not None:
            self.client.proxy = proxy

    async def register_session(self) -> None:
        """
        Registers a new session by creating a client, adding device information, and setting up the proxy.

        The method combines all steps to set up the Telegram client and session, including logging into the 
        Telegram API and sending a confirmation message.

        In case of an error, the error will be logged.
        """
        await self.add_device()
        await self._get_client()
        await self._get_proxy()
        try:
            await self._session_log()
            async with self.client as client:
                await client.send_message('me', '[OK] Authorization in Nexul!')
        except Exception as e:
            await self._erroe_log(error=e)