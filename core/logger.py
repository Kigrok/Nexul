from asyncio import to_thread
import logging

class Logger:
    COLORS: dict = {
        logging.DEBUG: '\x1b[38;5;27m',
        logging.INFO: '\x1b[38;5;34m',
        logging.WARNING: '\x1b[38;5;214m',
        logging.ERROR: '\x1b[38;5;196m',
        logging.CRITICAL: '\x1b[38;5;91m'}
    RESET: str = '\x1b[0m'

    def __init__(self, name: str, session: str, level: int = logging.INFO) -> None:
        self.session: str = session
        self.logger: int = self.setup_logger(name, level)

    def setup_logger(self, name: str, level: int) -> logging.Logger:
        logger: logging.Logger = logging.getLogger(name)
        logger.setLevel(level)  

        log_format: str = '\x1b[38;5;14m%(asctime)s\x1b[0m | %(colored_levelname)s | \x1b[38;5;119m%(name)s\x1b[0m | \x1b[38;5;200m%(session)s\x1b[0m | %(message)s'

        formatter: logging.Formatter = logging.Formatter(
            fmt=log_format, 
            datefmt='%H:%M:%S')
        
        if not logger.handlers:
            console_handler: logging.StreamHandler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(level) 
            logger.addHandler(console_handler)
        return logger

    def get_colored_levelname(self, level: int, levelname: str) -> str:
        color = self.COLORS.get(level, self.RESET)
        return f'{color}{levelname}{self.RESET}'

    async def log(self, level: int, msg: str, *args, **kwargs) -> None:
        await to_thread(self._log, level, msg, *args, **kwargs)

    def _log(self, level: int, msg: str, *args, **kwargs) -> None:
        extra: dict = {
            'colored_levelname': self.get_colored_levelname(
                level, 
                logging.getLevelName(level)),
            'session': self.session}
        match level:
            case logging.DEBUG:
                self.logger.debug(msg, *args, extra=extra, **kwargs)
            case logging.INFO:
                self.logger.info(msg, *args, extra=extra, **kwargs)
            case logging.WARNING:
                self.logger.warning(msg, *args, extra=extra, **kwargs)
            case logging.ERROR:
                self.logger.error(msg, *args, extra=extra, **kwargs)
            case logging.CRITICAL:
                self.logger.critical(msg, *args, extra=extra, **kwargs)


