import tls_client
import random
import time
import string
import os
import threading
import logging


logging.basicConfig(
    format=f"\033[33m(\033[37m%(asctime)s\x1b[38;5;9m\033[33m) \033[37m%(message)s\033[0m", 
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
)
logging.getLogger("Logger")


class DiscordJoinerPY:
    '''
    We love discord!!!

    This is the main class used by DiscordJoinerPY, an open-source tool.
    '''
    def __init__(self):
        self.client = tls_client.Session(
            client_identifier="chrome112",
            random_tls_extension_order=True
        )
        self.tokens = []
        self.proxies = []
        self.check()
    
    @staticmethod
    def headers(token: str) -> dict:
        '''
        Costruisce i parametri di intestazione aggiungendo il token all'interno di 'authorization'.

        Parametri:
            - token: str, il token da aggiungere all'intestazione.

        Restituisce:
            Un dizionario contenente i parametri di intestazione con il token aggiunto.

        Esempio:
            >>> DiscordJoinerPY.headers(token="my_token")
        '''
        headers = {
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
        return headers
    

    def get_cookies(self):
        '''
        Recupera i cookie dal client di Discord.

        Restituisce:
            Un dizionario contenente i cookies.
        '''
        cookies = {}
        try:
          response = self.client.get('https://discord.com')
          for cookie in response.cookies:
            if cookie.name.startswith('__') and cookie.name.endswith('uid'):
                cookies[cookie.name] = cookie.value
          return cookies
        
        except Exception as e:
          return cookies
    
    
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
                logging.info(f'Bypassed screen verification ({guild_id})')
            else:
                logging.info(f'Failed to bypass screen verification ({guild_id})')
        else:
            logging.info(f'Failed to find server screen verification ({guild_id})')

    def check_verification(self, token: str, invite: str, response, guild_id: str):
        if response.get("show_verification_form") == True:
            try:
              self.bypass_form(token=token, invite=invite, guild_id=guild_id)
            except:
               pass

    def accept_invite(self, token: str, invite: str, proxy_: str, guild_id: str):
        '''
        Simple full HTTP requests discord joiner
        
        You can bypass "session_id" by adding a random value (no need to use ws)
        '''
        payload = {
            'session_id': ''.join(random.choice(string.ascii_lowercase) + random.choice(string.digits) for _ in range(16))
        }

        proxy = {
            "http": "http://{}".format(proxy_),
            "https": "https://{}".format(proxy_)

        } if proxy_ else None

        try:
          response = self.client.post(
             url='https://discord.com/api/v9/invites/{}'.format(invite),
             headers=DiscordJoinerPY.headers(token=token),
             json=payload,
             cookies=self.get_cookies(),
             proxy=proxy
          )
          response_json = response.json()
          if response.status_code == 200:
              logging.info('Joined in {} ({})'.format(token, invite))
              self.check_verification(token=token, invite=invite,response=response_json, guild_id=guild_id)
          elif response.status_code == 401 and response_json['message'] == "401: Unauthorized":
              logging.info('Token is invalid ({})'.format(token))
          elif response.status_code == 403 and response_json['message'] == "You need to verify your account in order to perform this action.":
              logging.info('Token is locked ({})'.format(token))
          elif response.status_code == 400 and response_json['captcha_key'] == ['You need to update your app to join this server.']:
              logging.info('Captcha detected ({})'.format(token))
              #self.headers(token=token)['x-captcha-rqtoken'] = response_json['captcha_rqtoken']
              #self.headers(token=token)['x-captcha-key'] = captcha_token
          elif response_json['message'] == "404: Not Found":
              logging.info('Unknown invite ({})'.format(invite))
          else:
              logging.info('Invalid response ({})'.format(response_json))
        except Exception as error:
              logging.info('Error ({})'.format(error))


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
        try:
           self.load_tokens()
        except:
           pass


    def load_tokens(self):
        try:
          with open("./input/tokens.txt", "r") as file:
           for line in file:
             content = line.replace("\n",  "")
             self.tokens.append(content)

           self.start()
        except Exception as error:
            logging.info('Error ({})'.format(error))
    

    def load_proxies(self):
        try:
          with open("./input/proxies.txt", "r") as file:
           for line in file:
             content = line.replace("\n",  "")
             self.proxies.append(content)

        except Exception as error:
            logging.info('Error ({})'.format(error))
       

    def invite_manager(self, invite: str):
        if 'discord.gg' in invite or 'discord.com' in invite:
           invite = invite.replace('https://discord.com/invite/', '').replace('https://discord.gg/', '').replace('discord.gg/', '')

        try:
           response = self.client.get(f'https://discord.com/api/v9/invites/{invite}?inputValue{invite}&with_counts=true&with_expiration=true')
           if response.status_code == 200:
              response_json = response.json()
              guild = response_json.get('guild')
              return invite, guild.get('id')
        except Exception as e:
           pass
        

    def start(self):
        self.iterator = iter(self.proxies)
        self.load_proxies()

        invite = input("\033[33m(\033[37m{}\033[33m) \033[37mYour invite: ".format(time.strftime("%H:%M:%S")))
        try:
           invite, guild_id = self.invite_manager(invite=invite)
        except Exception as e:
           pass
        
        for token in self.tokens:
            try:
                if self.proxies == [] or self.proxies[0] == "/// Remove this line":
                   proxy = None
                else:
                   proxy = next(self.iterator)
                   logging.info('Using ({})'.format(proxy))

                threading.Thread(target=self.accept_invite, args=(token, invite, proxy, guild_id)).start()

            except Exception as error:
                logging.info('Error ({})'.format(error))
                
             
    
if __name__ == '__main__':
     # discord: swaps1337
     joiner = DiscordJoinerPY()
