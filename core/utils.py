from time import strftime, localtime
from re import search, compile
from uuid import UUID

class Utils:
    """
    A utility class providing methods for time conversion, UUID validation, and regex-based data extraction.

    Attributes:
        time_format (str): Format string used for converting timestamps to a formatted time string.
        tg_pattern (str): Regex pattern used for extracting Telegram WebApp data from URLs.
        device_pattern (str): Regex pattern used for extracting device information from user agent strings.
    """
    __slots__ = ('time_format', 'tg_pattern', 'device_pattern')

    def __init__(
            self, 
            time_format: str = '%H:%M:%S', 
            tg_pattern: str = (r'tgWebAppData=([^&]+)'), 
            device_pattern: str = (r'\(([^;]+);')):
        """
        Initializes the Utils class with the specified time format and regex patterns.
        Args:
            time_format (str): Format string used for converting timestamps (default is '%H:%M:%S').
            tg_pattern (str): Regex pattern used for extracting Telegram WebApp data from URLs (default is 'tgWebAppData=([^&]+)').
            device_pattern (str): Regex pattern used for extracting device information from user agent strings (default is '\(([^;]+);').
        """
        self.time_format: str = time_format
        self.tg_pattern: str = tg_pattern
        self.device_pattern: str = device_pattern

    async def convert_time(self, timestamp: int) -> str:
        """
        Converts a Unix timestamp (in milliseconds) into a formatted time string.
        Args:
            timestamp (int): The Unix timestamp in milliseconds to convert.
        Returns:
            str: The formatted time string based on the specified time_format.
        """
        return strftime(self.time_format, localtime(timestamp / 1000))

    async def valid_id(self, gameId: str) -> str:
        """
        Validates whether the provided string is a valid UUID version 4.
        Args:
            gameId (str): The game ID to validate.
        Returns:
            str: Returns the gameId if it is a valid UUIDv4.
        Raises:
            ValueError: If the gameId is not a valid UUIDv4 format.
        """
        try:
            if str(UUID(gameId, version=4)) == gameId:
                return gameId
            else:
                raise ValueError("Invalid UUIDv4 format")
        except ValueError:
            raise ValueError(f"Invalid gameId: {gameId}")

    async def regular(self, data: str) -> str:
        """
        Applies regex patterns to extract data based on predefined patterns.
        Args:
            data (str): The input data to be matched against patterns.
        Returns:
            str: Extracted data based on the matching pattern. Returns an empty string if no match is found.
        """
        match data:
            case _ if search(self.tg_pattern, data):
                return search(self.tg_pattern, data)
            case _ if search(self.device_pattern, data):
                return (compile(self.device_pattern).search(data)).group(1)
