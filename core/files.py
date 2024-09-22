import os, aiofiles.os, yaml, aiofiles, random, logging
from tqdm.asyncio import tqdm_asyncio
from fake_useragent import UserAgent
from core.utils import Utils
from core.types import ConfigDict, AppConfig
from core.register import Register
from core.telegram import Telegram
from core.logger import Logger

class Files:
    """
    The `Files` class is responsible for managing session files, configuration, and device-related operations 
    within the application. It provides methods for reading, updating, and validating session files, generating 
    random user agents and device models, and ensuring the integrity of session configurations.
    Attributes:
        sessions_path (``str``): Path to the directory where session files are stored.
        config_file (``str``): Path to the configuration file (in YAML format) that holds application settings.
        extension (``str``): The file extension used for session files (e.g., ".session").
        logger (``str``): A custom logger instance used for logging various actions and events during operations.
    """
    __slots__ = ('sessions_path', 'config_file', 'extension', 'logger')

    def __init__(
            self, 
            data: str = 'data', 
            sessions: str ='sessions', 
            config: str ='config.yml', 
            extension: str='.session') -> None:
        """
        Initializes the `Files` class with paths and configurations for session management.
        Parameters:
            data (``str``): The base directory where the session and config files are located. Defaults to 'data'.
            sessions (``str``): The subdirectory under `data` where session files are stored. Defaults to 'sessions'.
            config (``str``): The name of the configuration file (YAML format) that holds application settings. Defaults to 'config.yml'.
            extension (``str``): The file extension used for session files. Defaults to '.session'.
        Attributes:
            sessions_path (``str``): The full path to the directory containing session files, constructed from `data` and `sessions`.
            config_file (``str``): The full path to the configuration file, constructed from `data` and `config`.
            extension (``str``): The file extension for session files, used to filter session-related operations.
            logger (``Logger``): An instance of the `Logger` class for logging activity related to session and configuration management.
        """

        self.sessions_path: str = os.path.join(data, sessions)
        self.config_file: str = os.path.join(data, config)
        self.extension: str = extension
        self.logger: Logger = Logger(name='Files', session='')

    async def session_folder(self) -> None:
        """
        Asynchronously checks if the session folder exists, and if not, creates it.
        This method ensures that the directory for storing session files is present. 
        If the folder does not exist, it creates the necessary directory structure 
        and logs the creation action.
        """
        if not await aiofiles.os.path.exists(self.sessions_path):
            await aiofiles.os.makedirs(self.sessions_path)
            await self.logger.log(logging.DEBUG, 'Create sessions folder.')
    
    async def read_config(self) -> ConfigDict:
        """
        Asynchronously reads the configuration file and returns its content.
        This method opens the specified configuration file in read mode, loads its 
        contents as a dictionary using YAML, and logs the action.
        Returns:
            ** (``ConfigDict``): The contents of the configuration file as a dictionary.
        """
        async with aiofiles.open(self.config_file, mode='r') as file:
            await self.logger.log(logging.DEBUG, 'Read config file.')
            return yaml.safe_load(await file.read())
    
    async def update_config(self, content: any) -> None:
        """
        Asynchronously updates the configuration file with new content.
        This method writes the provided content to the configuration file in YAML format, 
        ensuring the output is in a readable block style. It then logs the update action.
        Args:
            content (``any``): The content to be written to the configuration file.
        """
        async with aiofiles.open(self.config_file, mode='w') as file:
            await file.write(yaml.dump(content, default_flow_style=False))
        await self.logger.log(logging.DEBUG, 'Update config file.')

    async def get_session_files(self) -> list[str]:
        """
        Asynchronously retrieves a list of session file names without extensions.
        This method scans the session folder for files that match the configured session file extension 
        and returns their names without the extension. A debug log is recorded upon execution.
        Returns:
            ** (``list``): A list of session file names (without extensions).
        """
        await self.logger.log(logging.DEBUG, 'Retrieves a list of all session files.')
        return [os.path.splitext(file)[0] for file 
            in await aiofiles.os.listdir(self.sessions_path) 
            if file.endswith(self.extension)]

    async def generate_device(
            self, 
            platform='mobile', 
            os='ios', 
            browser='safari') -> tuple[str, str]:
        """
        Asynchronously generates a random user agent and device model.
        This method creates a `UserAgent` instance configured with the specified platform, operating system, 
        and browser. It then generates a random user agent string and device model, which includes a 
        randomized device version and optional suffixes. A debug log is recorded upon execution.
        Parameters:
            platform (``str``): The platform for the user agent (default is 'mobile').
            os (``str``): The operating system for the user agent (default is 'ios').
            browser (``str``): The browser for the user agent (default is 'safari').
        Returns:
            ** (``tuple``): A tuple containing the generated user agent and device model:
        """
        ua: UserAgent = UserAgent(
            browsers=browser, 
            os=os, 
            platforms=platform)
        user_agent: str = (ua.random).strip()
        device_model: str = (' '.join([
            await Utils().regular(user_agent), 
            str(random.randint(11, 15)), 
            random.choice([' ', 'Pro', 'Max', 'Pro Max'])])).strip()
        await self.logger.log(logging.DEBUG, 'Generate a random user agent and device model.')
        return user_agent, device_model
    
    async def replace_device(self) -> None:
        """
        Asynchronously updates the device data in the configuration for sessions that have missing or incomplete
        device information.
        This method reads the current configuration file and identifies sessions where the `device_model` or
        `user_agent` fields are missing. For each of these sessions, it generates new device data and updates 
        the session's configuration. A debug log is recorded for each session that has its device data updated. 
        Finally, the configuration file is updated to reflect these changes.
        """
        config: ConfigDict = await self.read_config()
        modified_sessions: list[AppConfig] = [
            session for session in config.values() 
            if session.get('device_model') is None or session.get('user_agent') is None]
        if modified_sessions:
            for session in modified_sessions:
                session['user_agent'], session['device_model'] = await self.generate_device()
                await self.logger.log(logging.DEBUG, f"Updated device_data for session [{session.get('app_title')}].")
            await self.update_config(config)

    async def check_sessions(self) -> None:
        """
        Asynchronously checks the existence of session files for all configured sessions.
        This method iterates through all sessions defined in the configuration file. For each session, it constructs 
        the file path for the corresponding session file based on the session's title and the file extension. It then 
        checks if the session file exists in the specified session directory. If a session file is missing, it triggers 
        the registration of a new session by calling `Register(session=session).register_session()`.
        Debug logging is performed to indicate the start of the check process.
        """
        await self.logger.log(logging.DEBUG, 'Check if session files exist.')
        for _, session in (await self.read_config()).items():
            session_file_path: str = os.path.join(
                self.sessions_path, 
                session.get('app_title') + self.extension)        
            if not await aiofiles.os.path.exists(session_file_path):
                await Register(session=session).register_session()

    async def validate_sessions(self) -> None:
        """
        Asynchronously validates session files and cleans up invalid sessions.
        This method first disables INFO level logging to reduce verbosity during the validation process. It then 
        uses `tqdm_asyncio` to provide an asynchronous progress bar while iterating through the list of session files 
        retrieved by `get_session_files()`. For each session file, it calls the `cleanup` method to validate and, if 
        necessary, remove the file.
        After completing the validation and cleanup of session files, it re-enables logging and ensures that all session 
        files are checked by calling `check_sessions()`.
        """
        logging.disable(logging.INFO)
        try:
            async for _ in tqdm_asyncio(
                await self.get_session_files(), 
                desc='Validating', 
                unit='session',
                colour='cyan'):
                await self.cleanup(_)
        finally:
            logging.disable(logging.NOTSET)
            await self.check_sessions()

    async def cleanup(self, name: str) -> None:
        """
        Asynchronously cleans up an invalid session file.
        This method attempts to validate the session associated with the given `name` using the `Telegram` class. If the 
        session is determined to be invalid (i.e., `validate_session()` returns `False`), it removes the corresponding 
        session file from the filesystem. The file path is constructed using `self.sessions_path`, `name`, and 
        `self.extension`.
        After removing the file, the method logs an informational message indicating that the session file was removed.
        Args:
            name (``str``): The name of the session to be cleaned up.
        """

        if not await Telegram(
            name=name,
            proxy=await self.get_proxy(name=name)).validate_session():
            await aiofiles.os.remove(os.path.join(self.sessions_path, name + self.extension))
            await self.logger.log(logging.INFO, f'Removed invalid session file [{name}]')

    async def get_agent(self, name: str) -> str:
        """
        Asynchronously retrieves the user agent associated with a given application name.
        This method reads the configuration file and searches for the entry that matches the provided `name` (which 
        represents the application title). If a matching entry is found, it returns the corresponding user agent. If 
        no matching entry is found, it returns an empty string.
        Before performing the retrieval, the method logs a debug message indicating that it is attempting to get the user 
        agent for the specified `name`.
        Args:
            name (``str``): The application title for which the user agent is to be retrieved.
        Returns:
            ** (``str``): The user agent associated with the given application title, or an empty string if not found.
        """
        await self.logger.log(logging.DEBUG, f'Get user agent for [{name}].')
        return next(
            (session.get('user_agent', '') for session in 
            (await self.read_config()).values() 
            if session.get('app_title') == name),'')
    
    async def get_proxy(self, name: str) -> dict | None:
        """
        Asynchronously retrieves the proxy configuration associated with a given application name.
        This method reads the configuration file and searches for the entry that matches the provided `name` (which 
        represents the application title). If a matching entry is found, it returns the corresponding proxy configuration 
        as a dictionary. If no matching entry is found, it returns an empty dictionary.
        Before performing the retrieval, the method logs a debug message indicating that it is attempting to get the proxy 
        for the specified `name`.
        Args:
            name (``str``): The application title for which the proxy configuration is to be retrieved.
        Returns:
            ** (``dict | None``): The proxy configuration associated with the given application title, or an empty dictionary if not found.
        """
        await self.logger.log(logging.DEBUG, f'Get proxy for [{name}].')
        return next(
            (session.get('proxy', '') for session in 
            (await self.read_config()).values() 
            if session.get('app_title') == name),'')
    