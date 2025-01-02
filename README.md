## Nexul
[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=python)](https://www.python.org) ![Pyrogram version](https://img.shields.io/badge/Pyrogram-2.0.106-orange?logo=Pyrogram) [![aiofiles](https://img.shields.io/badge/aiofiles-24.1.0-blue?logo=aiofiles)](https://github.com/Tinche/aiofiles) [![certifi](https://img.shields.io/badge/certifi-2024.12.14-blue?logo=certifi)](https://github.com/certifi/python-certifi) [![cloudscraper](https://img.shields.io/badge/cloudscraper-1.2.71-orange?logo=cloudscraper)](https://github.com/venomous/cloudscraper) [![fake-useragent](https://img.shields.io/badge/fake-useragent?logo=fake-useragent)](https://github.com/fake-useragent/fake-useragent) [![PyYAML](https://img.shields.io/badge/PyYAML-6.0.2-blue?logo=PyYAML)](https://github.com/yaml/pyyaml) [![tqdm](https://img.shields.io/badge/tqdm-4.67.1-blue?logo=tqdm)](https://github.com/tqdm/tqdm) [![License](https://img.shields.io/badge/License-MIT-green)]()

**Nexul** is a tool for automating actions. It asynchronously manages multiple Telegram sessions for mini-applications within Telegram. 

---
## [Blum](https://t.me/blum/app?startapp=ref_vxdqZTfN8v)
![Blum](https://framerusercontent.com/images/N8XvRCQtMTDUKuSfLOhRGaQCxYY.jpg?lossless=1)
1. **Fetches Balance and Game Tickets**: Retrieves the current balance and the number of game tickets.
2. **Collects Daily Rewards**: Automatically collects daily rewards from the application.
3. **Claims Time-Based Rewards**: Claims rewards that become available over time.
4. **Claims Referral's Rewards**: Automatically collects rewards for referring other users.
~~5. **Plays Games**: Automates game playing within the app.~~
6. **Completion of tasks**: Performing social tasks (subscriptions, conversions).

Each session runs **asynchronously**, performing all tasks independently from other sessions at different times. Additionally, the claiming of rewards is done at **random intervals**, imitating real user behavior to avoid patterns that could trigger anti-bot systems.

---
## Installation

### Clone repository
```sh
git clone https://github.com/Kigrok/Nexul.git
cd Nexul
```

### Installing the virtual environment and packages

```sh
python3 -m venv .venv
source .venv/bin/activate
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