from typing import TypedDict, Optional, Dict

class ProxyConfig(TypedDict):
    """
    A TypedDict that defines the configuration for a proxy server.
    Attributes:
        scheme (``str``): The scheme of the proxy (e.g., 'http', 'https').
        hostname (``str``): The hostname or IP address of the proxy server.
        port (``int``): The port number to connect to on the proxy server.
        username (``Optional[str]``): Optional username for proxy authentication.
        password (``Optional[str]``): Optional password for proxy authentication.
    """
    scheme: str
    hostname: str
    port: int
    username: Optional[str]
    password: Optional[str]

class AppConfig(TypedDict):
    """
    A TypedDict that defines the application configuration.
    Attributes:
        api_id (``int``): The API ID for the app.
        api_hash (``str``): The API hash key for the app.
        app_title (``str``): The title of the application.
        phone_number (``str``): The phone number associated with the application.
        device_model (``Optional[str]``): Optional device model (for emulation purposes).
        user_agent (``Optional[str]``): Optional user agent string.
        proxy (``ProxyConfig``): The proxy configuration, defined as a ProxyConfig.
    """
    api_id: int
    api_hash: str
    app_title: str
    phone_number: str
    device_model: Optional[str]
    user_agent: Optional[str]
    proxy: Optional[ProxyConfig]

class ConfigDict(Dict[int, AppConfig]):
    """
    A dictionary where each key is an integer representing the config ID, 
    and the value is an AppConfig TypedDict containing the application settings.
    Example:
        config_dict = ConfigDict({
            1: {
                "api_id": 123456,
                "api_hash": "abc123",
                "app_title": "MyApp",
                "phone_number": "123456789",
                "device_model": "iPhone 16",
                "user_agent": "MyApp/1.0",
                "proxy": {
                    "scheme": "http",
                    "hostname": "proxy.example.com",
                    "port": 8080,
                    "username": None,
                    "password": None
                }
            }
        })
    """
    ...
