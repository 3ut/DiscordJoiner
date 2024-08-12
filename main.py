import tls_client
import random
import string
import os
import threading
import logging

from utils.log import Logger

class DiscordJoinerPY:
    def __init__(self):
        self.client = tls_client.Session(
            client_identifier="chrome112",
            random_tls_extension_order=True
        )
        self.log = Logger()
        self.tokens = []
        self.proxies = []
        self.check()

    @staticmethod
    def headers(token: str) -> dict:
        return {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': token,
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/channels/@me',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'x-context-properties': 'eyJsb2NhdGlvbiI6IkpvaW4gR3VpbGQiLCJsb2NhdGlvbl9ndWlsZF9pZCI6IjExMDQzNzg1NDMwNzg2Mzc1OTEiLCJsb2NhdGlvbl9jaGFubmVsX2lkIjoiMTEwNzI4NDk3MTkwMDYzMzIzMCIsImxvY2F0aW9uX2NoYW5uZWxfdHlwZSI6MH0=',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-GB',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6Iml0LUlUIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExMi4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTEyLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjE5MzkwNiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbCwiZGVzaWduX2lkIjowfQ==',
        }

    def get_cookies(self):
        try:
            response = self.client.get('https://discord.com')
            return {cookie.name: cookie.value for cookie in response.cookies}
        except Exception as e:
            self.log.info(f'Failed to obtain discord cookies [{e}]')
            return {}

    def bypass_form(self, token: str, invite: str, guild_id: str):
        headers = DiscordJoinerPY.headers(token=token)
        params = {
            'with_guild': 'false',
            'invite_code': invite,
        }

        verification_url = f'https://discord.com/api/v9/guilds/{guild_id}/member-verification'
        verification_response = self.client.get(url=verification_url, params=params, headers=headers)

        if verification_response.status_code == 200:
            verification_data = verification_response.json()
            put_url = f'https://discord.com/api/v9/guilds/{guild_id}/requests/@me'
            put_response = self.client.put(url=put_url, headers=headers, json=verification_data)

            if put_response.status_code == 201:
                self.log.info(f'Bypassed screen verification ({guild_id})')
            else:
                self.log.info(f'Failed to bypass screen verification ({guild_id})')
        else:
            self.log.info(f'Failed to find server screen verification ({guild_id})')

    def check_verification(self, token: str, invite: str, response: dict, guild_id: str):
        if response.get("show_verification_form"):
            try:
                self.bypass_form(token=token, invite=invite, guild_id=guild_id)
            except Exception as e:
                self.log.info(f'Error while bypassing form [{e}]')

    def handle_response(self, response, token: str, invite: str):
        status_code = response.status_code
        response_json = response.json()

        status_handlers = {
            200: lambda: self.log.info(f'Joined in {guild_id} [{token}]'),
            401: lambda: self.log.info(f'Token is invalid [{token}]'),
            403: lambda: self.log.info(f'Token is locked [{token}]'),
            400: lambda: self.log.info(f'Captcha detected [{token}]') if response_json.get('captcha_key') == ['You need to update your app to join this server.'] else self.log.info(f'Invalid response [{response_json}]'),
            404: lambda: self.log.info(f'Unknown invite [{invite}]'),
        }

        handler = status_handlers.get(status_code, lambda: self.log.info(f'Unexpected response [{response_json}]'))
        handler()

    def accept_invite(self, token: str, invite: str, proxy_: str, guild_id: str):
        payload = {
            'session_id': ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(16))
        }

        proxy = {
            "http": f"http://{proxy_}",
            "https": f"https://{proxy_}"
        } if proxy_ else None

        try:
            response = self.client.post(
                url=f'https://discord.com/api/v9/invites/{invite}',
                headers=DiscordJoinerPY.headers(token=token),
                json=payload,
                cookies=self.get_cookies(),
                proxy=proxy
            )
            self.handle_response(response, token, invite)
            self.check_verification(token=token, invite=invite, response=response.json(), guild_id=guild_id)
        except Exception as e:
            self.log.info(f'Error [{e}]')

    def check(self):
        folder_path = "input"
        file_path = os.path.join(folder_path, "tokens.txt")

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if not os.path.exists(file_path):
            for file_name in ['proxies.txt', 'tokens.txt']:
                file_path = os.path.join(folder_path, file_name)
                if not os.path.exists(file_path):
                    with open(file_path, "w") as file:
                        file.write("/// Remove this line")
        self.load_tokens()

    def load_tokens(self):
        try:
            with open("./input/tokens.txt", "r") as file:
                self.tokens = [line.strip() for line in file]
            self.start()
        except Exception as e:
            self.log.info(f'Error [{e}]')

    def load_proxies(self):
        try:
            with open("./input/proxies.txt", "r") as file:
                self.proxies = [line.strip() for line in file]
        except Exception as e:
            self.log.info(f'Error [{e}]')

    def invite_manager(self, invite: str) -> tuple:
        invite = invite.replace('https://discord.com/invite/', '').replace('https://discord.gg/', '').replace('discord.gg/', '')

        try:
            response = self.client.get(f'https://discord.com/api/v9/invites/{invite}?inputValue={invite}&with_counts=true&with_expiration=true')
            if response.status_code == 200:
                response_json = response.json()
                guild = response_json.get('guild')
                return invite, guild.get('id')
            else:
                self.log.info(f'Failed to obtain guild_id [{response.text}]')
                return '', ''
        except Exception as e:
            self.log.info(f'Error [{e}]')
            return '', ''

    def start(self):
        self.load_proxies()
        invite = self.log.inpt('Your discord invite: ')
        invite, guild_id = self.invite_manager(invite=invite)
        
        if not invite:
            exit(0)

        for token in self.tokens:
            try:
                proxy = next(iter(self.proxies), None)
                self.log.info(f'Using [{proxy}]') if proxy else None
                threading.Thread(target=self.accept_invite, args=(token, invite, proxy, guild_id)).start()
            except Exception as e:
                self.log.info(f'Error [{e}]')


if __name__ == '__main__':
    # discord: swaps1337
    joiner = DiscordJoinerPY()
