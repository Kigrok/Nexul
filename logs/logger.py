from logging import getLogger, Formatter, FileHandler, StreamHandler, Logger as CLogger, DEBUG, INFO, ERROR
from asyncio import to_thread
from os import path
from data import LOG_FILE

class Logger:
    """
    A class that provides logging functionality with both file and console outputs.
    
    This class allows for logging messages at different levels (DEBUG, INFO, ERROR) to both
    the console and a log file. The log file path is configured through the `LOG_FILE` constant,
    and the log format includes session information.

    Attributes:
        logger (``Logger``): The logger instance from Python's logging module.
        session (``str`` | ``None``): An optional session identifier that will be included in each log entry.
    """
    __slots__ = ('logger', 'session')

    formatter: Formatter = Formatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(session)s | %(message)s',
        datefmt='%d.%m.%y %H:%M:%S')

    def __init__(self, 
            name: str, 
            session: str | None = None, 
            level: int = DEBUG):
        """
        Initializes the Logger class with the provided logger name, session, and log level.

        Args:
            name (``str``): The name of the logger, typically the class or module name.
            session (``str`` | ``None``): Optional session identifier that will be included in log messages.
            level (``int``): The logging level (e.g., DEBUG, INFO, ERROR).
        """
        self.logger: CLogger = getLogger(name)
        self.logger.setLevel(level)
        self.session: str = session
        self.setup_handlers(level)

    def _file(self, level: int) -> FileHandler:
        """
        Creates and configures a file handler for logging.

        Args:
            level (``int``): The log level to use for the file handler.

        Returns:
            ``FileHandler``: Configured file handler for logging.
        """
        file: str = path.join(
            path.dirname(path.abspath(__file__)), 
            LOG_FILE)
        file_handler: FileHandler = FileHandler(file)
        file_handler.setLevel(level)
        file_handler.setFormatter(self.formatter)
        return file_handler

    def _console(self) -> StreamHandler:
        """
        Creates and configures a console handler for logging.

        Returns:
            ``StreamHandler``: Configured console handler for logging.
        """
        console_handler: StreamHandler = StreamHandler()
        console_handler.setLevel(INFO)
        console_handler.setFormatter(self.formatter)
        return console_handler

    def setup_handlers(self, level: int) -> None:
        """
        Sets up the logging handlers for both the file and console.

        This method clears any existing handlers and reconfigures them, ensuring both
        file and console logging is enabled.

        Args:
            level (``int``): The log level to use for the file handler.
        """
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        file_handler: FileHandler = self._file(level)
        if file_handler:
            self.logger.addHandler(file_handler)
        
        self.logger.addHandler(self._console())
        self.logger.propagate = False

    def _log(self, level: int, msg: str) -> None:
        """
        Logs a message at the specified level with the given message.

        This method is intended to be used internally and attaches the session information
        to the log message via the `extra` parameter.

        Args:
            level (``int``): The log level (DEBUG, INFO, ERROR).
            msg (``str``): The message to log.
        """
        extra: dict = {'session': self.session}
        self.logger.log(level, msg, extra=extra)

    async def log(self, level: int, message: str) -> None:
        """
        Asynchronously logs a message at the specified level.

        This method is a coroutine that runs the `_log` method in a separate thread to avoid blocking
        the asyncio event loop.

        Args:
            level (``int``): The log level (DEBUG, INFO, ERROR).
            message (``str``): The message to log.
        """
        await to_thread(self._log, level, message)

    async def log_info(self, message: str) -> None:
        """
        Asynchronously logs an INFO level message.

        Args:
            message (``str``): The message to log.
        """
        await self.log(level=INFO, message=message)
    
    async def log_debug(self, message: str) -> None:
        """
        Asynchronously logs a DEBUG level message.

        Args:
            message (``str``): The message to log.
        """
        await self.log(level=DEBUG, message=message)

    async def log_error(self, message: str) -> None:
        """
        Asynchronously logs an ERROR level message.

        Args:
            message (``str``): The message to log.
        """
        await self.log(level=ERROR, message=message)