from pyfiglet import Figlet
from tqdm.asyncio import tqdm_asyncio
from core.files import Files
from apps.blum.blum import Blum
from core.telegram import Telegram
from core.register import TGRegister
from asyncio import gather, run

async def _validate(name: str) -> None:
    """
    Validates the Telegram session by checking if it is still active.
    If not, it removes the session and re-registers it.

    Args:
        name (``str``): The session name to validate.
    """
    if not await Telegram(name=name).validate_session():
        await Files().remove_session(name=name)
        await TGRegister(name=name).register_session()

async def clear():
    """
    Clears invalid sessions by removing them from the session folder.
    This function checks for sessions in the folder that are not in the list of valid sessions.
    """
    for session in set(await Files().get_folder_sessions()) - set(await Files().get_sessions_names()):
        await Files().remove_session(name=session)

async def validate_sessions() -> None:
    """
    Validates all sessions by checking each one for activity. 
    If a session is invalid, it removes the session and registers it again.
    After all sessions are validated, it clears any outdated or invalid sessions.
    """
    for session in tqdm_asyncio(
            await Files().get_sessions_names(), 
            desc='Validating', unit='session',
            colour='cyan'):
        name: str = await Files().check_file_session(name=session)
        if name != None: await _validate(name=name)
        else: await TGRegister(name=session).register_session()
    await clear()

async def blum():
    """
    Continuously processes Blum tasks for each session present in the folder.
    This method is designed to run indefinitely, processing Blum tasks asynchronously.
    """
    while True:
        tasks: list = [
            Blum(name=session).main() for session in await Files().get_folder_sessions()]
        await gather(*tasks)

async def main():
    """
    The main entry point of the application. 
    Validates all sessions and runs Blum tasks concurrently.
    """
    await validate_sessions()
    await gather(blum())

def banner() -> None:
    """
    Prints the application banner using the 'Nexul' text in an isometric font with a color scheme.
    This adds a visual identity to the app upon startup.
    """
    print('\x1b[38;5;199m'+
        (Figlet(font='isometric1')).renderText('Nexul')+
        '\x1b[0m')
    print('\tCreated by \x1b[38;5;85mhttps://github.com/Kigrok\x1b[0m\n')

if __name__ == '__main__':
    banner()
    run(main())