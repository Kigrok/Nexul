from core.files import Files
import logging, json, asyncio
from core.logger import Logger
from core.telegram import Telegram
from core.utils import Utils
from cloudscraper import CloudScraper, create_scraper
from aiohttp import ClientSession, ClientResponseError, TCPConnector, BasicAuth, ClientTimeout, ClientResponse
from random import randint, uniform
import inspect

class Blum:
    __slots__ = ('name', 'session', 'refresh_token', 'logger', 'proxy', 'proxy_auth', 'endTime', 'game', 'logger')

    app_name: str = 'BlumCryptoBot'
    app_url: str = 'https://telegram.blum.codes/'

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.session: ClientSession = None
        self.refresh_token: str = None
        self.proxy = None
        self.proxy_auth = None
        self.logger: Logger = Logger(name='Blum', session=self.name)
        self.endTime: int = 1
        self.game: int = 0

    async def urls(self, request: str) -> str:
        game: str = 'https://game-domain.blum.codes/api/v1/'
        user: str = 'https://user-domain.blum.codes/api/v1/'
        match request:
            case 'auth':
                return user + 'auth/provider/PROVIDER_TELEGRAM_MINI_APP'
            case 'refresh':
                return user + 'auth/refresh'
            case 'balance':
                return game + 'user/balance'
            case 'friends_balance':
                return user + 'friends/balance'
            case 'claim_friends':
                return user + 'friends/claim'
            case 'game_play':
                return game + 'game/play'
            case 'claim_game':
                return game + 'game/claim'
            case 'farming_start':
                return game + 'farming/start'
            case 'farming_claim':
                return game + 'farming/claim'
            case 'daily':
                return game + 'daily-reward?offset=420'
            case 'now':
                return game + 'time/now'

    async def _get_data(self) -> dict:
        await self.logger.log(logging.DEBUG, 'Get and convert telegram data.')
        return {
            'query': await Telegram(
                name=self.name, 
                proxy=None).get_data(
                    app=self.app_name, 
                    url=self.app_url)}

    async def _save_tokens(self, data: dict) -> None:
        match inspect.stack()[1].function:
            case 'login':
                await self.logger.log(logging.DEBUG, 'Save tokens in "login".')
                access: str = data.get('token').get('access')
                refresh: str = data.get('token').get('refresh')
            case 'refresh':
                await self.logger.log(logging.DEBUG, 'Save tokens in "refresh".')
                access: str = data.get('access')
                refresh: str = data.get('refresh')
        self.session.headers['Authorization'] = 'Bearer ' + access
        self.refresh_token: str = refresh

    async def _content_type(self, response: ClientResponse):
        if 'application/json' in response.headers.get('Content-Type', ''):
            return await response.json()
        else:
            return await response.text()

    async def make_request(self, method, url, data=None):
        try:
            match method:
                case 'get':
                    async with self.session.get(
                        url=url,
                        proxy=self.proxy,
                        proxy_auth=self.proxy_auth) as response:
                        response.raise_for_status()
                        await self.logger.log(logging.DEBUG, f'Get request to: {url}.')
                        return await self._content_type(response=response)
                case 'post':
                    async with self.session.post(
                        url=url,
                        json=data,
                        proxy=self.proxy,
                        proxy_auth=self.proxy_auth) as response:
                        response.raise_for_status()
                        await self.logger.log(logging.DEBUG, f'Post request to: {url}.')
                        return await self._content_type(response=response)
        except asyncio.TimeoutError:
            await self.logger.log(logging.ERROR, 'Request timed out.')
            await self.refresh()
        except ClientResponseError as e:
            await self.logger.log(logging.ERROR, f'HTTP error: {e}')
            await self.refresh()
        except Exception as e:
            await self.logger.log(logging.ERROR, f"An unexpected error occurred: {e}")
            await self.refresh()

    async def login(self) -> None:
        await self._save_tokens(
            await self.make_request(
                method='post', 
                url=await self.urls('auth'), 
                data=await self._get_data()))
        await self.logger.log(logging.DEBUG, 'Login to app.')

    async def refresh(self):
        data: dict = {'refresh': self.refresh_token}
        await self._save_tokens(
            await self.make_request(
                method='post', 
                url=await self.urls('refresh'), 
                data=data))
        await self.logger.log(logging.DEBUG, 'Refresh tokens.')
        
    async def balance(self):
        await self._balance_data(
            await self.make_request(
                method='get', 
                url=await self.urls('balance')))
        await self.logger.log(logging.DEBUG, 'Get balance.')

    async def _balance_data(self, data: dict):
        balance: float = data.get('availableBalance', 0)
        self.game: int = data.get('playPasses', 0)
        self.endTime: int = int(data.get('farming', {}).get('endTime', 0))
        await self.logger.log(
            logging.INFO, 
            f'Balance: \x1b[38;5;227m{balance}\x1b[0m | Games: \x1b[38;5;227m{self.game}\x1b[0m')
        
    async def daily(self) -> None:
        async with self.session.get(
            url=await self.urls('daily')) as response:
            await self.logger.log(logging.DEBUG, 'Get request to daily info.')
            if response.status == 200:
                data: dict = (await response.json()).get('days')[-1]
                days: int = data.get('original')
                games: int = (data.get('reward')).get('passes')
                points: int = (data.get('reward')).get('points')
                await self._daily_claim(days, games, points)

    async def _daily_claim(self, days: int, games: int, points: int) -> None:
        async with self.session.post(
            url=await self.urls('daily'),
            proxy=self.proxy,
            proxy_auth=self.proxy_auth) as response:
            await self.logger.log(logging.DEBUG, 'Post request to daily.')
            if response.status == 200:
                await self.logger.log(
                    logging.INFO, 
                    f'Claim Daily | Day: \x1b[38;5;227m{days}\x1b[0m | Games: \x1b[38;5;227m{games}\x1b[0m | Points: \x1b[38;5;227m{points}\x1b[0m')
        
    async def _now(self) -> int:
        data: dict = await self.make_request(
            method='get', 
            url=await self.urls('now'))
        await self.logger.log(logging.DEBUG, 'Get "now" time.')
        return data.get('now')
    
    async def _claim_farm(self) -> None:
        data: dict = await self.make_request(
            method='post', 
            url=await self.urls('farming_claim'))
        await self.logger.log(
            logging.INFO, 
            f'Claim points | Balance: \x1b[38;5;227m{data.get('availableBalance')}\x1b[0m')
        
    async def _start_farm(self) -> int:
        data: dict = await self.make_request(
            method='post', 
            url=await self.urls('farming_start'))
        await self.logger.log(logging.DEBUG, 'Start farming points.')
        return data.get('endTime')

    async def farm(self) -> None:
        if int(self.endTime) < int(await self._now()):
            await self._claim_farm()
            await asyncio.sleep(1)
            time: int = await self._start_farm()
            time_conv: str = await Utils().convert_time(timestamp=time)
            await self.logger.log(
                logging.INFO, 
                f'Claim at \x1b[38;5;97m{time_conv}\x1b[0m')
            
    async def _friends_data(self, data: dict) -> tuple[int, bool, int, int]:
        balance: float = data.get('amountForClaim', 0)
        canClaim: bool = data.get('canClaim', False)
        friends: int = data.get('usedInvitation', 0)
        time: str = data.get('canClaimAt', 0)
        await self.logger.log(logging.DEBUG, 'Get friends data.')
        return balance, canClaim, friends, time
    
    async def _claim_friends(self) -> None:
        data: dict = await self.make_request(method='post', url=await self.urls('claim_friends'))
        await self.logger.log(
            logging.INFO, 
            f'Claim friend points: \x1b[38;5;227m{data.get('claimBalance')}\x1b[0m')
            
    async def friends_balance(self) -> None:
        data: dict = await self.make_request(method='get', url=await self.urls('friends_balance'))
        balance, canClaim, friends, time = await self._friends_data(data=data)
        if balance != 0 and friends != 0:
            if canClaim:
                await self._claim_friends()
            else:
                time: str = await Utils().convert_time(timestamp=time)
                await self.logger.log(
                    logging.INFO, 
                    f'Friends: \x1b[38;5;227m{friends}\x1b[0m | Points: \x1b[38;5;227m{balance}\x1b[0m | Claim at \x1b[38;5;97m{time}\x1b[0m')
                
    async def _play_game(self) -> str:
        data: dict = await self.make_request(
            method='post', 
            url=await self.urls('game_play'))
        await self.logger.log(logging.DEBUG, 'Playing game.')
        return data.get('gameId')
    
    async def _claim_game(self, gameId: str) -> None:
        points: int = randint(180, 230)
        data: dict = {
            'gameId': gameId, 
            'points': points}
        await self.make_request(
            method='post', 
            url=await self.urls('claim_game'),
            data=data)
        await self.logger.log(
            logging.INFO, 
            f'Complete Game | Points: \x1b[38;5;227m{points}\x1b[0m')
                
    async def games(self) -> None:
        range_game: int = randint(1, 15)
        if int(self.game) >= int(range_game):
            await self.logger.log(
                logging.INFO, 
                f'Start playing for \x1b[38;5;227m{range_game}\x1b[0m games.')
            for _ in range(range_game):
                gameId: str = await Utils().valid_id(await self._play_game())
                await asyncio.sleep(uniform(30, 40))
                await self._claim_game(gameId=gameId)
                await asyncio.sleep(uniform(2, 5))
        
    async def generate_proxy(self):
        proxy: dict = await Files().get_proxy(name=self.name)
        await self.logger.log(logging.DEBUG, 'Generate proxy.')
        if proxy is not None:
            self.proxy_auth: BasicAuth = BasicAuth(
                login=proxy.get('username'), 
                password=proxy.get('password'))
            self.proxy: str = f'{proxy.get('http')}://{proxy.get('hostname')}:{proxy.get('port')}'

    async def _blum_active(self):
        await self.generate_proxy()
        await self.login()
        await asyncio.sleep(1)
        await self.refresh()
        await self.balance()
        await asyncio.sleep(1)
        await self.daily()
        await asyncio.sleep(1)
        await self.farm()
        await asyncio.sleep(1)
        await self.friends_balance()
        await asyncio.sleep(1)
        await self.games()


    async def main(self) -> None:
        time: int = randint(40, 130)*60
        try:
            scraper: CloudScraper = create_scraper()
            headers: dict = {
                **scraper.headers,
                'Cache-Control': 'no-cache',
                'Origin': self.app_url,
                'Pragma': 'no-cache',
                'Priority': 'u=1, i',
                'User-Agent': await Files().get_agent(name=self.name)}
            async with ClientSession(
                headers=headers, 
                timeout=ClientTimeout(20),
                connector=TCPConnector(ssl=False)) as session:
                self.session: ClientSession = session
                await self.logger.log(
                    logging.INFO, 
                    f'Session sleep for \x1b[38;5;97m{int(time/60)}\x1b[0m min.')
                await asyncio.sleep(time)
                await self._blum_active()
        except ClientResponseError as e:
            await self.logger.log(logging.ERROR, f'HTTP error: {e}')
        except asyncio.TimeoutError:
            await self.logger.log(logging.ERROR, 'Request timed out.')
        except Exception as e:
            await self.logger.log(logging.ERROR, f"An unexpected error occurred: {e}")