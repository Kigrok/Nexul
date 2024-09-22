## Nexul
[![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?&logo=python&logoColor=python)](https://www.python.org) [![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0.106-orange)](https://docs.pyrogram.org/) ![aiofiles](https://img.shields.io/badge/aiofiles-24.1.0-blue) [![aiohttp](https://img.shields.io/static/v1?label=aiohttp&message=3.10.5&logo=Aiohttp&colorColor=Aiohttp)](https://docs.aiohttp.org/en/stable/) [![cloudscraper](https://img.shields.io/badge/cloudscraper-GitHub-orange)](https://github.com/venomous/cloudscraper) ![tqdm](https://img.shields.io/static/v1?label=tqdm&message=4.66.5&logo=tqdm&colorColor=tqdm) [![License](https://img.shields.io/badge/License-MIT-green)]()

**Nexul** is a tool for automating actions. It asynchronously manages multiple Telegram sessions for mini-applications within Telegram. 

---
## [Blum](https://t.me/blum/app?startapp=ref_vxdqZTfN8v)
![Blum](https://framerusercontent.com/images/N8XvRCQtMTDUKuSfLOhRGaQCxYY.jpg?lossless=1)
1. **Fetches Balance and Game Tickets**: Retrieves the current balance and the number of game tickets.
2. **Collects Daily Rewards**: Automatically collects daily rewards from the application.
3. **Claims Time-Based Rewards**: Claims rewards that become available over time.
4. **Claims Referral Rewards**: Automatically collects rewards for referring other users.
5. **Plays Games**: Automates game playing within the app.

Each session runs **asynchronously**, performing all tasks independently from other sessions at different times. Additionally, the claiming of rewards is done at **random intervals**, imitating real user behavior to avoid patterns that could trigger anti-bot systems.

---
## Install 

### Clone repository
```sh
git clone https://github.com/Kigrok/Nexul.git
cd Nexul
```

### Installing the virtual environment and packages

```sh
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

### Add to `config.yml` telegram account
1.  Log in [Telegram](https://my.telegram.org/auth).
2.  Create App.
3.  Add to config file `Nexul/data/config.yml` 'api_id', 'api_hash', 'app_title', 'phone_number', 'proxy'.

Example of adding an account with proxy settings
If you have a proxy, you can add it to the config.yml file as follows:
```yaml
0:
  api_hash: YOUR_API_HASH
  api_id: YOUR_API_ID
  app_title: YOUR_APP_TITLE
  device_model: null
  phone_number: YOUR_PHONE_NUMBER # without "+"; 123456789
  proxy:     
    hostname: 12.456.78.912
    password: password
    port: 8000
    scheme: http or socks5
    username: username
  user_agent: null
```
If you don’t have a proxy, set it as follows:
```yaml
proxy: null
```
**Note**: `user_agent` and `device_model` will be generated automatically by Nexul.

---
# Start

```sh
python3 main.py
```