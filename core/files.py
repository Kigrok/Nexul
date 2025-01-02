from data import CONFIG_FILE, SESSIONS, DATA
from core.types import Config, AccountConfig, ProxyType
from os import path, getcwd
from yaml import safe_load as ysafe_load, dump as ydump
from json import loads as jloads, dumps as jdumps
from aiofiles.os import path as apath, makedirs as amakedirs, remove as aremove, listdir as alistdir
from aiofiles import open as aopen

class Files:
    """
    A utility class for handling file operations asynchronously, including YAML and JSON file operations,
    session file management, and data directory organization.

    This class provides abstraction for working with configurations, sessions, and data storage.

    Attributes:
        None (no instance-specific attributes due to the use of `__slots__`).
    """
    __slots__ = ()
    
    @property
    def data_dir(self) -> str:
        """
        Path to the main data directory.

        Returns:
            ``str``: Absolute path to the data directory.
        """
        return path.join(getcwd(), DATA)

    @property
    def sessions_dir(self) -> str:
        """
        Path to the sessions directory inside the data directory.

        Returns:
            ``str``: Absolute path to the sessions directory.
        """
        return path.join(self.data_dir, SESSIONS)
    
    @property
    def config_file(self) -> str:
        """
        Path to the configuration file.

        Returns:
            ``str``: Absolute path to the configuration file.
        """
        return path.join(self.data_dir, CONFIG_FILE)

    async def _file_exists(self, path: str) -> bool:
        """
        Checks if a file exists.

        Args:
            path (``str``): Path to the file.

        Returns:
            ``bool``: True if the file exists, False otherwise.
        """
        return await apath.exists(path)

    async def session_folder(self) -> None:
        """
        Ensures that the sessions folder exists. Creates it if it doesn't.
        """
        if not await self._file_exists(self.sessions_dir):
            await amakedirs(self.sessions_dir)

    async def read_yaml(self) -> Config:
        """
        Reads the YAML configuration file.

        Returns:
            ``Config``: Parsed content of the YAML file.
        """
        async with aopen(self.config_file, mode='r') as file:
            return ysafe_load(await file.read())
        
    async def update_yaml(self, content: dict) -> None:
        """
        Updates the YAML configuration file with new content.

        Args:
            content (``dict``): Data to write into the YAML file.
        """
        async with aopen(self.config_file, mode='w') as file:
            await file.write(ydump(content, default_flow_style=False))

    async def get_sessions_names(self, filter: str = 'app_title') -> list:
        """
        Retrieves the names of sessions based on a filter.

        Args:
            filter (``str``): The key to filter session data by. Defaults to 'app_title'.

        Returns:
            ``list``: List of session names matching the filter.
        """
        return list(session.get(filter) for session in (await self.read_yaml()).values())
  
    async def get_folder_sessions(self) -> list:
        """
        Retrieves the list of session files in the sessions folder.

        Returns:
            ``list``: List of session file names without extensions.
        """
        files: list = await alistdir(self.sessions_dir)
        return list(path.splitext(file)[0] for file in files if file.endswith(f'.session'))

    async def get_info(self, name: str, filter: str) -> ProxyType | str | None:
        """
        Retrieves specific information from a session by name.

        Args:
            name (``str``): The session name.
            filter (``str``): The key to retrieve from the session.

        Returns:
            ``ProxyType`` | ``str`` | ``None``: The value corresponding to the filter, or None if not found.
        """
        return next((session.get(filter) for session in (await self.read_yaml()).values()
            if session.get('app_title') == name), None)
    
    async def get_session_data(self, name: str) -> AccountConfig | None:
        """
        Retrieves all data for a specific session by name.

        Args:
            name (``str``): The session name.

        Returns:
            ``AccountConfig`` | ``None``: The session data, or None if not found.
        """
        return next((session for session in (await self.read_yaml()).values()
            if session.get('app_title') == name), None)
    
    async def _session_file_path(self, name: str) -> str:
        """
        Generates the path to a session file by name.

        Args:
            name (``str``): The session name.

        Returns:
            ``str``: Path to the session file.
        """
        return path.join(self.sessions_dir, name + f'.session')
    
    async def check_file_session(self, name: str) -> str | None:
        """
        Checks if a session file exists.

        Args:
            name (``str``): The session name.

        Returns:
            ``str`` | ``None``: Session name if the file exists, otherwise None.
        """
        if await self._file_exists(await self._session_file_path(name=name)):
            return name
        
    async def remove_session(self, name: str) -> None:
        """
        Deletes a session file by name.

        Args:
            name (``str``): The session name.
        """
        await aremove(await self._session_file_path(name=name))

    async def read_json(self, path: str) -> dict:
        """
        Reads a JSON file.

        Args:
            path (``str``): Path to the JSON file.

        Returns:
            ``dict``: Parsed JSON content.
        """
        async with aopen(path, mode='r') as file:
            return jloads(await file.read())
        
    async def _file_path(self, name: str, extension: str = '.json') -> str:
        """
        Generates a file path for a given name and extension.

        Args:
            name (``str``): File name.
            extension (``str``): File extension. Defaults to '.json'.

        Returns:
            ``str``: Full file path.
        """
        return path.join(self.data_dir, name + extension)
    
    async def save_json(self, name: str, data: dict) -> None:
        """
        Saves data to a JSON file.

        Args:
            name (``str``): File name.
            data (``dict``): Data to save.
        """
        async with aopen(await self._file_path(name=name), mode='w') as file:
            await file.write(jdumps(data))
        
    async def save_image(self, content: bytes, name: str) -> None:
        """
        Saves image content to a file.

        Args:
            content (``bytes``): Image content as bytes.
            name (``str``): File name.
        """
        async with aopen(await self._file_path(name=name, extension='.png'), mode='wb') as file:
            await file.write(content)

    async def get_file_value(self, file: str, id: str) -> str | None:
        """
        Retrieves a value from a JSON file based on an ID.

        Args:
            file (``str``): File name.
            id (``str``): ID to search for.

        Returns:
            ``str`` | ``None``: The value corresponding to the ID, or None if not found.
        """
        return next(task['value'] for task in await self.read_json(path=await self._file_path(name=file))
            if task['id'] == id)