from pyrogram.raw.functions.messages import RequestWebView
from pyrogram import Client, errors
from urllib.parse import unquote
from core.logger import Logger
from core.utils import Utils
from re import search
from os import path
import logging

class Telegram:
    """
    Handles interactions with Telegram through the Pyrogram library, including session validation and data retrieval.
    This class is responsible for managing a Telegram client instance, which can be used to interact with Telegram's API. 
    It includes methods to validate the current session and retrieve data from specific URLs within Telegram. The client 
    can be configured with an optional proxy.
    Attributes:
        name (``str``): The name associated with the Telegram client.
        workdir (``str``): The directory path where session data is stored.
        proxy (``dict | None``): The proxy settings to be used by the Telegram client, if any.
        client (``Client``): The Pyrogram client instance used to interact with Telegram.
        logger (``Logger``): An instance of the Logger class used for logging various events and errors.
    """
    __slots__ = ('name', 'workdir', 'client', 'proxy', 'logger')

    def __init__(
            self, 
            name: str, 
            proxy: dict| None, 
            data: str = 'data', 
            sessions: str = 'sessions') -> None:
        """
        Initializes a Telegram client with optional proxy settings and sets up a logger.
        Parameters:
            name (``str``): The name to be assigned to the Telegram client.
            proxy (``dict | None``): Optional dictionary containing proxy settings. If None, no proxy is used.
            data (``str``): Directory where session data is stored (default is 'data').
            sessions (``str``): Subdirectory within 'data' where session files are located (default is 'sessions').
        Attributes:
            name (``str``): The name associated with the Telegram client.
            workdir (``str``): The path to the directory where session data is stored, constructed from 'data' and 'sessions'.
            proxy (``dict | None``): The proxy settings to be used by the Telegram client, if any.
            client (``Client``): An instance of the Pyrogram Client initialized with the given name and workdir.
            logger (``Logger``): An instance of the Logger class for logging various events related to the Telegram client.
        """
        self.name: str = name
        self.workdir: str = path.join(data, sessions)
        self.proxy: dict | None = proxy
        self.client: Client = Client(
                name=self.name,
                workdir=self.workdir)
        self.logger: Logger = Logger(name='Telegram', session=self.name)
        if proxy is not None:
            self.client.proxy = self.proxy            

    async def validate_session(self) -> bool:
        """
        Validates the current Telegram session by attempting to retrieve the client's information.
        This method checks if the session is active and valid by using the `get_me` method of the Pyrogram Client.
        If the session is valid, it logs a success message and returns True. If there is an RPC error or any other
        exception during the validation, it logs an appropriate error message and returns False.
        Returns:
            ** (``bool``): True if the session is valid, False otherwise.
        """
        try:
            async with self.client as client:
                await client.get_me()
                await self.logger.log(logging.DEBUG, 'Session validation successful.')
                return True
        except errors.RPCError as e:
            await self.logger.log(logging.ERROR, f'Session validation failed: {e}')
            return False
        except Exception as e:
            await self.logger.log(logging.ERROR, f'An unexpected error occurred during session validation: {e}')
            return False

    async def get_data(
            self, 
            app: str, 
            url: str, 
            platform: str ='ios') -> str:
        """
        Retrieves web data from a specified URL within the context of a Telegram session.
        This method uses the Pyrogram Client to invoke a web view request, which allows interaction with a web page
        within the Telegram app. It attempts to resolve the peer and bot references, and then fetches the web page
        data. Upon successful retrieval, it extracts data from the URL and logs a success message.
        Parameters:
            app (``str``): The name of the application or bot for which the web view is requested.
            url (``str``): The URL from which to retrieve data.
            platform (``str``): The platform for which the web view is requested (default is 'ios').
        Returns:
            ** (``str``): The extracted data from the URL.
        Raises:
            Exception: If there is any error while retrieving or processing the web data, an error is logged and the exception is raised.
        """
        try:
            async with self.client as client:
                web_view = await client.invoke(RequestWebView(
                    peer=await client.resolve_peer(app),
                    bot=await client.resolve_peer(app),
                    platform=platform,
                    from_bot_menu=True,
                    url=url))
                await self.logger.log(logging.DEBUG, f'Successfully retrieved web data for session in [{app}]')
                return await self._extract_data_from_url(web_view.url)
        except Exception as e:
            await self.logger.log(logging.ERROR, f'Error getting Telegram web data in [{app}]: {e}')
            raise

    async def _extract_data_from_url(self, url: str) -> str:
        """
        Extracts and decodes data from a given URL.
        This method takes a URL as input and uses a utility function to extract relevant data from the URL. The data
        is then URL-decoded twice to handle double encoding. If data extraction is successful, it logs a success message
        and returns the decoded data. If no data is found, it logs an error message.
        Parameters:
            url (``str``): The URL from which to extract data.
        Returns:
            ** (``str``): The extracted and decoded data from the URL.
        Raises:
            None: Logs an error if no data is found but does not raise an exception.
        """
        await self.logger.log(logging.DEBUG, f'Extracting data from URL.')
        match: str = await Utils().regular(data=url)
        if match:
            extract_data: str = unquote(unquote(match.group(1)))
            await self.logger.log(logging.DEBUG, 'Data extracted successfully.')
            return extract_data
        else:
            await self.logger.log(logging.ERROR, f'No data found in URL: {url}')
