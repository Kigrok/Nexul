from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from pyrogram.raw.functions.account import UpdateStatus
from pyrogram.raw.types import InputBotAppShortName, InputPeerUser, AppWebViewResultUrl
from pyrogram.raw.functions.messages import RequestWebView, RequestAppWebView
from uvloop import install as uinstall
from asyncio import sleep as asleep
from core.files import Files
from core.proxy import Proxy
from core.utils import Utils
from core.types import ProxyType
from logs import Logger

class Telegram:
    """
    A class that handles Telegram client management using the Pyrogram library.

    This class provides methods to:
    - Create and configure a Telegram client.
    - Keep the client online and ensure session validity.
    - Interact with Telegram bots and retrieve web data or app data.

    Attributes:
        __name (str): The name of the session used to manage configuration and logs.
        client (Client): The instance of the Pyrogram client for interacting with Telegram.
        logger (Logger): The logger instance for logging errors and information.
    """

    def __init__(self, name: str) -> None:
        """
        Initializes the Telegram class with the provided session name and configures the logger.

        Args:
            name (``str``): The session name used for logging and file management.
        """
        self.__name: str = name
        self.client: Client = None
        self.logger: Logger = Logger(
            name=__class__.__name__, 
            session=self.__name)
        uinstall() # Install uvloop for improved asyncio performance

    @property
    def workdir(self) -> str:
        """
        Property to get the session's working directory.

        Returns:
            ``str``: The path to the session's working directory.
        """
        return Files().sessions_dir
    
    async def _get_proxy(self) -> None:
        """
        Configures the proxy settings for the client.

        This method checks if a proxy is configured for the session and applies it to the client.
        """
        proxy: ProxyType | None = await Proxy(name=self.__name).get_tg_proxy()
        if proxy is not None:
            self.client.proxy = proxy

    async def _create_client(self) -> None:
        """
        Creates a new Telegram client if it doesn't exist.

        This method initializes the `Client` instance using session configuration, sets the language code,
        and applies any configured proxy settings.
        """
        if self.client is None:
            self.client: Client = Client(
                name=self.__name, 
                workdir=self.workdir, 
                lang_code='en')
            await self._get_proxy()

    async def keep_alive(self) -> None:
        """
        Keeps the client online by updating its status.

        This method sends an update to Telegram to set the client's status to 'online'.
        """
        try:
            await self.client.invoke(UpdateStatus(offline=False))
        except Exception as e:
            await self.logger.log_error(f'Failed to update online status: {e}')

    async def ensure_subscription(self, channel: str = 'venvnft') -> None:
        """
        Ensures that the client is subscribed to a specific channel.

        This method checks if the client is a member of the specified channel and updates the online status.
        
        Args:
            channel (``str``): The name of the channel to check subscription for (default is 'venvnft').
        """
        await self._create_client()
        async with self.client:
            await self.client.get_chat_member(
                (await self.client.get_chat(channel)).id, 
                (await self.client.get_me()).id)
            await self.keep_alive()

    async def validate_session(self) -> bool:
        """
        Validates the current session by checking if the client can access its own details.

        This method ensures that the session is active by attempting to get the client's own details 
        and updating its online status.

        Returns:
            ``bool``: `True` if the session is valid, `False` otherwise.
        """
        await self._create_client()
        try:
            async with self.client:
                await self.client.get_me()
                await self.keep_alive()
                return True
        except RPCError as e:
            await self.logger.log_error(f'Session validation failed: {e}')
            return False
        except Exception as e:
            await self.logger.log_error(f'An unexpected error occurred during session validation: {e}')
            return False
        
    async def get_web_data(self, app: str, url: str, platform: str = 'ios') -> str:
        """
        Retrieves web data from a Telegram bot or application.

        This method interacts with a bot to retrieve a URL, which can be used to display web content.
        
        Args:
            app (``str``): The name or username of the bot.
            url (``str``): The URL to request web data from.
            platform (``str``): The platform for which the request is made (default is 'ios').

        Returns:
            ``str``: The resulting URL from the web view request.
        """
        await self._create_client()
        try:
            async with self.client:
                peer: InputPeerUser = await self.client.resolve_peer(app)
                web_view: AppWebViewResultUrl = await self.client.invoke(RequestWebView(
                    peer=peer, bot=peer, platform=platform, 
                    from_bot_menu=True,url=url))
                await self.keep_alive()
                return web_view.url
        except FloodWait as e:
            await asleep(1)
            return await self.get_web_data(app, url, platform) 
        except Exception as e:
            await self.logger.log_error(f'Error getting Telegram web data in [{app}]: {e}')

    async def get_app_data(self, app: str, platform: str = 'ios') -> str:
        """
        Retrieves app data from a Telegram bot.

        This method retrieves data from a Telegram bot using the `RequestAppWebView` function to interact 
        with the bot and obtain its response.

        Args:
            app (``str``): The name or username of the bot.
            platform (``str``): The platform for which the request is made (default is 'ios').

        Returns:
            ``str``: The resulting URL from the app data request, processed by the `Utils` class.
        """
        await self._create_client()
        try:
            async with self.client:
                peer: InputPeerUser = await self.client.resolve_peer(app)
                input_bot_app: InputBotAppShortName = InputBotAppShortName(bot_id=peer, short_name='app')
                web_view: AppWebViewResultUrl = await self.client.invoke(RequestAppWebView(
                    peer=peer, app=input_bot_app,
                    platform=platform, write_allowed=True))
                await self.keep_alive()
                return await Utils(name=self.__name).regular(web_view.url)
        except FloodWait as e:
            await asleep(1)
            return await self.get_app_data(app, platform)  
        except Exception as e:
            await self.logger.log_error(f'Error getting Telegram web app data in [{app}]: {e}')
            raise