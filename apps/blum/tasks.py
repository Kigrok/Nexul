from apps.blum.data import BlumData
from core.web import Web
from core.files import Files
from core.telegram import Telegram
from logs import Logger
from random import randint, uniform
from asyncio import sleep as asleep

class BlumTasks:
    """
    This class handles task-related operations for Blum.
    It fetches tasks and delegates their processing to the `Tasks` class.

    Attributes:
        name (``str``): The name of the Blum session.
        web (``Web``): Instance of the Web class for handling HTTP requests.
    """
    __slots__ = ('name', 'web')

    def __init__(self, name: str, web: Web) -> None:
        """
        Initializes a BlumTasks instance.

        Args:
            name (``str``): The name of the Blum session.
            web (``Web``): Instance of the Web class for HTTP interactions.
        """
        self.name: str = name
        self.web: Web = web

    @property
    def url(self) -> str:
        """
        URL property for retrieving tasks.

        Returns:
            ``str``: The endpoint for Blum tasks.
        """
        return BlumData.tasks

    async def tasks(self) -> list:
        """
        Fetches the list of tasks from the BlumData API.

        Returns:
            ``list``: A list of tasks retrieved from the API.
        """
        return await self.web.get_data(url=self.url)
    
    async def work_task(self, tasks: list) -> None:
        """
        Processes a given list of tasks by invoking the `main` method of the `Tasks` class.

        Args:
            tasks (``list``): A list of tasks to be processed.
        """
        await Tasks(name=self.name, web=self.web, tasks=tasks).main()

class Tasks:
    """
    This class handles the detailed processing of individual and grouped tasks.

    Attributes:
        name (``str``): The name of the session.
        web (``Web``): Instance of the Web class for HTTP requests.
        tasks (``list``): List of tasks to process.
        logger (``Logger``): Logger instance for recording task events.
    """
    __slots__ = ('name', 'web', 'tasks', 'logger')

    def __init__(self, name: str, web: Web, tasks: list) -> None:
        """
        Initializes a Tasks instance.

        Args:
            name (``str``): The name of the session.
            web (``Web``): Instance of the Web class for HTTP interactions.
            tasks (``list``): List of tasks to process.
        """
        self.name: str = name
        self.web: Web = web
        self.tasks: list = tasks
        self.logger: Logger = Logger(
            name=__class__.__name__,
            session=self.name)
        
    @property
    def url(self) -> str:
        """
        Property to retrieve the URL for Blum tasks.

        Returns:
            ``str``: The endpoint URL for accessing Blum tasks.
        """
        return BlumData.tasks

    async def _random_tasks(self, tasks: list) -> dict:
        """
        Selects a random task from a given list of tasks.

        Args:
            tasks (``list``): A list of tasks.

        Returns:
            ``dict``: A randomly selected task, or None if the list is empty.
        """
        match len(tasks):
            case 0: return 
            case 1: return tasks[0]
            case _: return tasks[randint(0, len(self.tasks) - 1)]
    
    async def section_type(self, data: dict) -> None:
        """
        Processes tasks based on their section type.

        Args:
            data (``dict``): Task data containing section information.
        """
        section_type: str = data.get('sectionType', None)
        match section_type:
            case 'HIGHLIGHTS' | 'WEEKLY_ROUTINE': 
                tasks: dict = await self._random_tasks(data.get('tasks', []))
                await self.task_type(data=tasks)
            case 'DEFAULT':
                tasks: dict = await self._random_tasks(tasks=data.get('subSections', {}))
                await self.default_type(data=tasks)

    async def task_type(self, data: dict) -> None:
        """
        Processes tasks based on their type.

        Args:
            data (``dict``): Task data containing task type information.
        """
        match data.get('type', None):
            case 'SOCIAL_SUBSCRIPTION': await self.status_type(data)
            case 'GROUP': await self.sub_tasks(data=data.get('subTasks', []))
            case 'PROGRESS_TARGET': await self.status_progres(task=data)

    async def status_progres(self, task: dict) -> None:
        """
        Checks the progress of a task and initiates further actions if the target is met.

        Args:
            task (``dict``): Task data containing progress details.
        """
        progress_target: dict = task.get('progressTarget', {})
        target: int = int(progress_target.get('target', 100000) or 100000)
        progress: int = int(progress_target.get('progress', 0) or 0)
        if progress >= target: await self.status_type(data=task)

    async def sub_tasks(self, data: list) -> None:
        """
        Iterates through a list of subtasks and processes each.

        Args:
            data (``list``): A list of subtasks to be processed.
        """
        for task in data: await self.status_type(data=task)

    async def status_type(self, data: dict) -> None:
        """
        Handles task actions based on their current status.

        Args:
            data (``dict``): Task data containing status information.
        """
        match data.get('status', 'FINISHED'):
            case 'NOT_STARTED':
                await self.start_task(data)
            case 'READY_FOR_VERIFY': 
                await self.verify_task(data=data)
            case 'READY_FOR_CLAIM': 
                await self.claim_task(data=data)

    async def default_type(self, data: dict) -> None:
        """
        Processes tasks based on their default type, such as social or academy tasks.

        Args:
            data (``dict``): Task data containing default type information.
        """
        match data.get('title', None):
            case 'Blum Bits' | 'Farming' | 'New' | 'Frens' | 'Academy':  
                tasks: dict = await self._random_tasks(tasks=data.get('tasks', []))
                await self.task_type(data=tasks)
            case 'Socials': 
                tasks: list = data.get('tasks', [])
                await self.sub_tasks(data=tasks)

    async def execution_on_tg(self, url: str) -> None:
        """
        Subscribes to a Telegram channel based on the provided URL.

        Args:
            url (``str``): The Telegram channel URL.
        """
        channel: str = url.split('https://t.me/')[1]
        if '/' not in channel:
            await Telegram(name=self.name).ensure_subscription(channel=channel)
            await self.logger.log_info(f'Subscribe to @{channel}')

    async def execution_on_web(self, url: str) -> dict:
        """
        Sends a GET request to the provided URL and returns the response.

        Args:
            url (``str``): The URL for the web execution.

        Returns:
            ``dict``: Response data from the web request.
        """
        return await self.web._get_request(url=url)

    async def execution_task(self, data: dict) -> None:
        """
        Executes a task either on Telegram or via a web request.

        Args:
            data (``dict``): Task data containing execution details.
        """
        intg: bool = data.get('socialSubscription', {}).get('openInTelegram', False)
        url: str = data.get('socialSubscription', {}).get('url', '')
        match intg:
            case True: await self.execution_on_tg(url=url)
            case False: await self.execution_on_web(url=url)

    async def start_task(self, data: dict) -> None:
        """
        Initiates a task and logs the action.

        Args:
            data (``dict``): Task data for the task to be started.
        """
        idx: str = data.get('id')
        title: str = data.get('title', '')
        reward: int = data.get('reward', 0)
        url: str = f'{self.url}/{idx}/start'
        await self.logger.log_info(f'Start Task: {title} | Reward: {reward}')
        await self.web.post_data(url=url, data=None)
        await self.execution_task(data=data)
        await asleep(uniform(5, 10))

    async def verify_task(self, data: dict) -> None:
        """
        Validates a task using the provided keyword and logs the result.

        Args:
            data (``dict``): Task data for the task to be verified.
        """
        idx: str = data.get('id')
        url: str = f'{self.url}/{idx}/validate'
        keyword: str = await Files().get_file_value(file='blum', id=idx)
        if keyword is not None:
            result: dict = await self.web.post_data(url=url, data={'keyword': keyword})
            title: str = result.get('title', '')
            status: str = result.get('status', '')
            await self.logger.log_info(f'Task: {title} - {status}')
        await asleep(uniform(5, 10))
        await self.claim_task(data=data)

    async def claim_task(self, data: dict) -> None:
        """
        Claims the reward for a task and logs the outcome.

        Args:
            data (``dict``): Task data for the task to be claimed.
        """
        idx: str = data.get('id')
        url: str = f'{self.url}/{idx}/claim'
        data: dict = await self.web.post_data(url=url, data=None)
        if data.get('status', '') == 'FINISHED':
            title: str = data.get('title', '')
            reward: int = data.get('reward', 0)
            await self.logger.log_info(f'Claim Task: {title} | Reward: {reward}')
            
    async def main(self) -> None:
        """
        Main method to process the tasks by invoking the section type handler.
        """
        await self.section_type(data=await self._random_tasks(tasks=self.tasks))
