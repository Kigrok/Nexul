from time import strftime, localtime
from re import search
from random import choice, randint
from fake_useragent import UserAgent
from urllib.parse import unquote
from logs import Logger
from core.files import Files
from core.types import Config
from logging import DEBUG
from asyncio import sleep as asleep

class Utils:
    """
    A utility class providing various helper functions for time conversion, random data generation, device simulation, and more.

    This class offers methods to:
    - Convert timestamps into human-readable formats.
    - Randomly generate device models and user-agent strings.
    - Extract specific data from strings.
    - Sleep for a random amount of time within a specified range.

    Attributes:
        __name (``str``): The name of the session (typically used for logging purposes).
    """
    __slots__ = ('__name')

    def __init__(self, name: str) -> None:
        """
        Initializes the utility class with the provided session name.

        Args:
            name (``str``): The name of the session used for logging and managing configuration.
        """
        self.__name: str = name
        
    async def convert_time(self, timestamp: int, format: str = '%H:%M:%S', seconds: int = 1000) -> str:
        """
        Converts a given timestamp (in milliseconds) into a human-readable time format.

        Args:
            timestamp (``int``): The timestamp (in milliseconds).
            format (``str``): The desired time format (default is '%H:%M:%S').
            seconds (``int``): The divisor for converting milliseconds to seconds (default is 1000).

        Returns:
            ``str``: The formatted time string.
        """
        return strftime(format, localtime(int(timestamp) / int(seconds)))
    
    async def convert_minutes(self, minutes: int, seconds: int = 60) -> tuple[int, int]:
        """
        Converts the given number of minutes into hours and remaining minutes.

        Args:
            minutes (``int``): The total number of minutes.
            seconds (``int``): The number of seconds in a minute (default is 60).

        Returns:
            tuple (``int``, ``int``): The number of hours and remaining minutes.
        """
        hours: int = minutes // seconds  
        minutes: int = minutes % seconds  
        return hours, minutes
    
    async def regular(self, data: str) -> str:
        """
        Extracts and decodes the 'tgWebAppData' parameter from a given URL string.

        Args:
            data (``str``): The URL or string containing the 'tgWebAppData' parameter.

        Returns:
            ``str``: The decoded value of the 'tgWebAppData' parameter.
        """
        tg_pattern: str = (r'tgWebAppData=([^&]+)')
        result: str = search(tg_pattern, data)
        return str(unquote(result.group(1)))

    async def get_random_value(self, dict: dict) -> tuple[int, str]: 
        """
        Selects a random key-value pair from a dictionary.

        Args:
            dict (``dict``): The dictionary to pick a random key-value pair from.

        Returns:
            tuple (``int``, ``str``): The randomly selected key (as integer) and value (as string).
        """
        key: str = choice(list(dict.keys()))
        value: str = dict[key]
        return int(key), value
    
    async def generate_phone(self) -> str:
        """
        Generates a random iPhone model name.

        Returns:
            ``str``: A random iPhone model string (e.g., 'iPhone 12 Pro').
        """
        return (' '.join([
            'iPhone', 
            str(randint(11, 16)), 
            choice([' ', 'Pro', 'Max', 'Pro Max'])])).strip()
    
    async def generate_device(self) -> tuple[str, str]:
        """
        Generates a random user-agent string and device model.

        Returns:
            tuple (``str``, ``str``): A tuple containing the user-agent string and the device model.
        """
        ua: UserAgent = UserAgent(browsers='Mobile Safari')
        user_agent: str = (ua.safari).strip()
        device: str = await self.generate_phone()
        return user_agent, device
    
    async def add_device(self):
        """
        Updates the session data with a newly generated device model and user-agent.

        This method generates a new device model and user-agent, and updates the session configuration 
        by saving the new data to the YAML file.
        """
        user_agent, device = await self.generate_device()
        files: Files = Files()
        data: Config = await files.read_yaml()
        for _, session_data in (data).items():
            session_data['device_model'] = device
            session_data['user_agent'] = user_agent
        await files.update_yaml(data)

    async def _sleep(self, min_sleep: int, max_sleep: int, seconds: int = 60) -> None:
        """
        Pauses the execution for a random amount of time between min_sleep and max_sleep.

        Args:
            min_sleep (``int``): The minimum amount of time (in minutes) to sleep.
            max_sleep (``int``): The maximum amount of time (in minutes) to sleep.
            seconds (``int``): The number of seconds in a minute (default is 60).

        This function logs the sleep time and then sleeps asynchronously for the generated time in seconds.
        """
        sleep_time: int = randint(min_sleep, max_sleep)
        hours, minutes = await self.convert_minutes(minutes=sleep_time)
        await Logger(name=__class__.__name__, session=self.__name).log_debug(
            f'Session sleep for {hours} hour(s) {minutes} minute(s)')
        await asleep(sleep_time * seconds)