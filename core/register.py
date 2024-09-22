from pyrogram import Client, errors
from core.types import AppConfig
from core.logger import Logger
from os import path
import logging

class Register:
    """
    Handles the registration of a Telegram session using the Pyrogram client.
    The `Register` class is responsible for initializing the Telegram client with the provided session configuration
    and handling the registration process. It includes methods for setting up the client, managing errors, and
    logging relevant information throughout the registration process.
    Attributes:
        api_id (``int``): The API ID used for client authorization.
        api_hash (``str``): The API hash used for client authorization.
        app_title (``str``): The title of the application associated with the session.
        phone_number (``str``): The phone number used for client authentication.
        device_model (``str``): The device model used for the client session.
        workdir (``str``): Directory path for storing session files.
        client (``Client``): An instance of the Pyrogram `Client` used for interacting with Telegram.
        proxy (``dict | None``): Optional proxy configuration for the client.
        logger (``Logger``): An instance of the `Logger` class for logging events related to the registration process.
    """
    __slots__ = ('api_id', 'api_hash', 'app_title', 'phone_number', 'device_model', 'workdir', 'client', 'proxy', 'logger')

    def __init__(self, session: AppConfig) -> None:
        """
        Initializes the `Register` class with configuration details for a Telegram session.
        Parameters:
            session (``AppConfig``): A configuration object containing details required for Telegram client initialization.
        Attributes:
            api_id (``int``): Stores the API ID extracted from the session configuration.
            api_hash (``str``): Stores the API hash extracted from the session configuration.
            app_title (``str``): Stores the application title extracted from the session configuration.
            phone_number (``str``): Stores the phone number extracted from the session configuration.
            proxy (``dict | None``): Stores the optional proxy settings extracted from the session configuration.
            device_model (``str``): Stores the device model extracted from the session configuration.
            workdir (``str``): Directory path for storing session files, set to 'data/sessions'.
            client (``Client``): An instance of the Pyrogram `Client` initialized with the provided configuration.
            logger (``Logger``): An instance of the `Logger` class for logging events related to the registration process.
        Note:
            - The `Client` instance is configured with `hide_password=True` to prevent displaying the password in logs.
            - If a proxy is provided, it is set for the `Client` instance.
        """
        self.api_id: int = session.get('api_id')
        self.api_hash: str = session.get('api_hash')
        self.app_title: str = session.get('app_title')
        self.phone_number: str = str(session.get('phone_number'))
        self.proxy: dict | None = session.get('proxy')
        self.device_model: str = session.get('device_model')
        self.workdir: str = path.join('data', 'sessions')
        self.client: Client = Client(
                name=self.app_title,
                api_id=self.api_id,
                api_hash=self.api_hash,
                phone_number=self.phone_number,
                device_model=self.device_model,
                workdir=self.workdir,
                hide_password=True)
        self.logger: Logger = Logger(
            name='Telegram Register', 
            session=self.app_title)
        if self.proxy is not None:
            self.client.proxy = self.proxy

    async def register_session(self):
        """
        Registers a new Telegram session and handles various errors that may occur during the process.
        This method performs the following steps:
        1. Logs the start of the session registration process at the DEBUG level.
        2. Attempts to create a new session by sending a message to the user's "me" chat to confirm successful authorization.
        3. Handles specific errors that may arise during the session registration process and logs them accordingly:
            - `FloodWait`: Raised when the server imposes a wait time due to too many requests; logs an error and advises waiting.
            - `RPCError`: General error for RPC issues; logs the error message.
            - `AuthKeyDuplicated`: Raised when the authentication key is duplicated; logs the error message.
            - `AuthKeyUnregistered`: Raised when the authentication key is unregistered; logs the error message.
            - `AuthTokenExpired`: Raised when the authentication token has expired; logs the error message.
            - `PhoneCodeInvalid`: Raised when an invalid phone code is provided; logs the error message.
            - `PhoneCodeExpired`: Raised when the phone code has expired; logs the error message.
            - `PhoneNumberBanned`: Raised when the phone number is banned; logs the error message.
            - `SessionPasswordNeeded`: Raised when a session password is required but not provided; logs the error message.
            - `UserAlreadyParticipant`: Raised when the user is already a participant; logs the error message.
            - `PeerIdInvalid`: Raised when the peer ID is invalid; logs the error message.
            - Catches all other unexpected exceptions and logs them as errors.
        """

        await self.logger.log(logging.DEBUG, "Starting session registration.")
        try:
            await self.logger.log(logging.INFO, f'Create new session.')
            async with self.client:
                await self.client.send_message("me", "[OK] Authorization in Nexul!")
        except errors.FloodWait as e:
            await self.logger.log(logging.ERROR, f'Flood wait error: {e}. Please wait and try again later.')
        except errors.RPCError as e:
            await self.logger.log(logging.ERROR, f'RPC error: {e}.')
        # except errors.NetworkError as e:
        #     await self.logger.log(logging.ERROR, f'Network error: {e}.')
        except errors.AuthKeyDuplicated as e:
            await self.logger.log(logging.ERROR, f'Auth key duplicated error: {e}.')
        except errors.AuthKeyUnregistered as e:
            await self.logger.log(logging.ERROR, f'Auth key unregistered error: {e}.')
        except errors.AuthTokenExpired as e:
            await self.logger.log(logging.ERROR, f'Auth token expired error: {e}.')
        except errors.PhoneCodeInvalid as e:
            await self.logger.log(logging.ERROR, f'Phone code invalid error: {e}.')
        except errors.PhoneCodeExpired as e:
            await self.logger.log(logging.ERROR, f'Phone code expired error: {e}.')
        except errors.PhoneNumberBanned as e:
            await self.logger.log(logging.ERROR, f'Phone number banned error: {e}.')
        except errors.SessionPasswordNeeded as e:
            await self.logger.log(logging.ERROR, f'Session password needed error: {e}.')
        except errors.UserAlreadyParticipant as e:
            await self.logger.log(logging.ERROR, f'User already participant error: {e}.')
        except errors.PeerIdInvalid as e:
            await self.logger.log(logging.ERROR, f'Peer ID invalid error: {e}.')
        except Exception as e:
            await self.logger.log(logging.ERROR, f'An unexpected error occurred: {e}.')
