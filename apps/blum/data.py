class BlumData:
    """
    BlumData contains constants and configuration details for interacting with the Blum application APIs.
    This includes URLs for various domains (user, tribe, wallet, game, mempad) and associated endpoints.

    Attributes:
        referralToken (``str``): Referral token for the application.
        my_tribe (``str``): Default tribe name for the user.
        app_name (``str``): Name of the application.
        app_url (``str``): URL of the application.
        
    Private Attributes:
        __game (``str``): Base URL for game-related API endpoints.
        __user (``str``): Base URL for user-related API endpoints.
        __tribe (``str``): Base URL for tribe-related API endpoints.
        __wallet (``str``): Base URL for wallet-related API endpoints.
        __game2 (``str``): Base URL for game-related API endpoints (version 2).
        __mempad (``str``): Base URL for mempad-related API endpoints.

    Public Attributes:
        me (``str``): Endpoint to retrieve the current user's details.
        login (``dict[str, str]``): Authentication endpoints for login and refresh.
        game (``dict[str, str]``): Endpoints for game-related actions.
        daily (``str``): Endpoint for daily rewards.
        frens (``dict[str, str]``): Endpoints for friend-related actions.
        tasks (``str``): Endpoint for retrieving tasks.
        tribe (``dict[str, str]``): Endpoints for tribe-related actions.
        wallet (``dict[str, str]``): Endpoints for wallet-related actions.
        mempad (``dict[str, str]``): Endpoints for mempad-related actions.
    """
    
    referralToken: str = 'vxdqZTfN8v'
    my_tribe: str = 'venvnft'
    
    app_name: str = 'BlumCryptoBot'
    app_url: str = 'https://telegram.blum.codes/'

    __game: str = 'https://game-domain.blum.codes/api/v1/'
    __user: str = 'https://user-domain.blum.codes/api/v1/'
    __tribe: str = 'https://tribe-domain.blum.codes/api/v1/tribe/'
    __wallet: str = 'https://wallet-domain.blum.codes/api/v1/wallet/'
    __game2: str = 'https://game-domain.blum.codes/api/v2/'
    __mempad: str = 'https://mempad-domain.blum.codes/api/v1/jetton/'

    me: str = f'{__user}user/me'

    login: dict[str, str] = {
        'auth_url': f'{__user}auth/provider/PROVIDER_TELEGRAM_MINI_APP',
        'refresh': f'{__user}auth/refresh'}

    game: dict[str, str] = {
        'now': f'{__game}time/now',
        'balance': f'{__game}user/balance',
        'farm_claim': f'{__game}farming/claim',
        'farm_start': f'{__game}farming/start'}
    
    daily: str = f'{__game2}daily-reward'

    frens: dict[str, str] = {
        'friends_balance': f'{__user}friends/balance',
        'friends_trading': f'{__user}friends/trading',
        'friends_page': f'{__user}friends?pageSize=1000',
        'friends_claim': f'{__user}friends/claim'}
    
    tasks: str = 'https://earn-domain.blum.codes/api/v1/tasks'

    tribe: dict[str, str] = {
        'tribe_my': f'{__tribe}my',
        'tribe_bot': f'{__tribe}bot',
        'leaderboard': f'{__tribe}leaderboard',
        'tribes': __tribe,
        'search_tribe': f'https://tribe-domain.blum.codes/api/v1/tribe?search=',
        'chatname': f'{__tribe}by-chatname/'}
    
    wallet: dict[str, str] = {
        'wallet_my': f'{__wallet}my',
        'usd': f'{__wallet}my/balance?fiat=usd',
        'points_balance': f'{__wallet}my/points/balance',
        'history': f'{__wallet}my/points/actions_history'}

    mempad: dict[str, str] = {
        'partner': f'{__mempad}partner',
        'created_at': f'{__mempad}top/created_at?published=exclude',
        'spotlight': f'{__mempad}spotlight',
        'live': f'{__mempad}live',
        'rate': f'{__mempad}rate',
        'transactions': f'{__mempad}top/transactions?published=include',
        'nearest_to_listing': f'{__mempad}top/nearest_to_listing?published=include_listed',
        'published_at': f'{__mempad}top/published_at?published=only',
        'market_cap': f'{__mempad}top/market_cap?published=include',
        'positions': f'{__mempad}positions?address='}

