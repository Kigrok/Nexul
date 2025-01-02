from typing import TypedDict, Optional, ReadOnly

class WebProxy(TypedDict):
    http: ReadOnly[str]
    https: ReadOnly[str]

class ProxyType(TypedDict):
    hostname: ReadOnly[str]
    password: ReadOnly[str]
    port: ReadOnly[int]
    scheme: ReadOnly[str]
    username: ReadOnly[str]

class AccountConfig(TypedDict):
    api_hash: ReadOnly[str]
    api_id: ReadOnly[int]
    app_title: ReadOnly[str]
    password: ReadOnly[str]
    device_model: str
    phone_number: ReadOnly[str]
    proxy: Optional[ProxyType]
    user_agent: str

class Config(TypedDict):
    account_id: ReadOnly[AccountConfig]