from core.files import Files
from pyfiglet import Figlet
from apps.blum import Blum
from asyncio import run, gather
from random import randint

async def work_files():
    """
    Handles the file management workflow by:
    - Ensuring the session folder exists.
    - Replacing missing device information in the configuration.
    - Checking if all required session files are present.
    - Validating the existing session files and removing any invalid ones.
    """
    await Files().session_folder()
    await Files().replace_device()
    await Files().check_sessions()
    await Files().validate_sessions()

async def blum():
    """
    Creates and runs Blum instances for each session retrieved from the session files.
    Uses asyncio.gather to run all the Blum tasks concurrently.
    """
    while True:
        tasks: list = [
            Blum(name=session).main() for session in await Files().get_session_files()]
        await gather(*tasks)

async def main():
    """
    Orchestrates the main workflow:
    - Executes the file operations (work_files).
    - Initiates the Blum processes (blum).
    """
    await work_files()
    await blum()

def banner() -> None:
    """
    Prints the application banner using the 'Nexul' text in an isometric font with a color scheme.
    This adds a visual identity to the app upon startup.
    """
    print('\x1b[38;5;199m'+
        (Figlet(font='isometric1')).renderText('Nexul')+
        '\x1b[0m')
    print('\tCreated by \x1b[38;5;85mhttps://github.com/Kigrok\x1b[0m\n')

if __name__=='__main__':
    banner()
    run(main())