# Made by Celentroft
# Github: https://github.com/Celentroft/token-checker

import os
import time
import requests
import sys
from colorama import Fore, init
from datetime import datetime

init(autoreset=True)

class TokenChecker:
    def __init__(self):
        self.valids = 0
        self.invalids = 0
        self.locked = 0
        self.rate = 0
        self.nitro_boost = 0
        self.nitro_classic = 0
        self.Y = Fore.YELLOW
        self.W = Fore.WHITE
        self.G = Fore.GREEN
        self.R = Fore.RED
        self.C = Fore.CYAN
        self.V = Fore.MAGENTA

    def gettime(self):
        return datetime.now().strftime("%H:%M:%S")

    def clear(self):
        return os.system('cls' if os.name == 'nt' else 'clear')

    def init_checker(self):
        output_files = ["invalids.txt", "valid.txt", "locked.txt"]
        self.clear()
        choice = input(f"{self.V}[?] Do you want to clear old output files (yes/no)?: ")
        if choice.lower() == "yes":
            for filename in output_files:
                with open(f"data/{filename}", 'w') as f:
                    pass
            print(f"{self.G}[+] All old output files are cleared. Let's check your tokens.")
            time.sleep(2)
        return True

    def check_file_content(self, file_path):
        with open(file_path, 'r') as f:
            if len(f.read().splitlines()) == 0:
                self.clear()
                input(f"{self.Y}[!] No Tokens Found in file '{file_path}' Press Enter To Continue...")
                return False
            else:
                with open(file_path, 'r') as f:
                    return f.read().splitlines()

    def check_verify(self, content):
        ev = "YES" if content.get('verified') else "NO"
        fv = "YES" if content.get('phone') else "NO"
        return ev, fv

    def get_req_code(self, token):
        headers = {"Authorization": token}
        req = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
        if req.status_code == 200:
            response = req.json()
            ev, fv = self.check_verify(response)
            boost = False
            nitro_type = None
            if response.get('premium_type') == 1:
                nitro_type = "Nitro Basic"
                self.nitro_classic += 1
            elif response.get('premium_type') == 2:
                nitro_type = "Nitro Boost"
                self.nitro_boost += 1
                boost = self.check_boost(token)
            else:
                nitro_type = "No Nitro"
            return "valid", nitro_type, ev, fv, boost
        elif req.status_code == 403:
            return "locked", False, False, False, False
        elif req.status_code == 429:
            return "rate limited", False, False, False, False
        else:
            return "invalid", False, False, False, False

    def check_boost(self, token):
        headers = {"Authorization": token}
        req = requests.get('https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots', headers=headers)
        return sum(1 for item in req.json() if item.get('premium_guild_subscription') is not None) 

    def check_nitro_ending(self, token):
        headers = {"Authorization": token}
        req = requests.get('https://discord.com/api/v9/users/@me/billing/subscriptions', headers=headers)
        if req.status_code == 200:
            return 30 - datetime.fromisoformat(req.json()[0].get("current_period_end")).day 
        
    def save_into_file(self, file_path, token):
        try:
            with open(file_path, 'a') as f:
                f.write(token + "\n")
            return True 
        except Exception as e:
            return False

    def main(self):
        self.init_checker()
        tokens = self.check_file_content("data/tokens.txt")
        if tokens == False:
            return sys.exit(1)
        self.clear()
        print(f'Output Format: {self.W}(Hour){self.G}[+] Token Checked Token.. {self.W}[{self.V}Nitro Type{self.W}][{self.V}DAY LEFT{self.W}][{self.V}EV{self.W}][{self.V}FV{self.W}][{self.V}Active Boost{self.W}] Time Taken: in sec\n')
        for token in tokens:
            sys.stdout.write(f'\x1b]2;{self.valids} Valids / {self.locked} Locked / {self.invalids} Invalids\x07')

            token = token.strip()
            now = time.time()
            status, nitro_type, ev, fv, boost = self.get_req_code(token)
            if status == "valid":
                self.valids += 1
                save = self.save_into_file("data/valid.txt", token)
                if save:
                    if nitro_type == "Nitro Boost":
                        ending = self.check_nitro_ending(token)
                        print(f'{self.W}({self.gettime()}){self.G}[+] Token {token[:24]}.**.*** {self.W}[{self.V}{nitro_type}{self.W}][{self.V}{ending} DAY LEFT{self.W}][{self.V}{ev}{self.W}][{self.V}{fv}{self.W}][{self.V}{boost} USED{self.W}] Time Taken: {time.time() - now:.2f} sec')
                    elif nitro_type == "Nitro Basic":
                        print(f'{self.W}({self.gettime()}){self.G}[+] Token {token[:24]}.**.*** {self.W}[{self.V}{nitro_type}{self.W}][{self.V}{ending} DAY LEFT{self.W}][{self.V}{ev}{self.W}][{self.V}{fv}{self.W}] Time Taken: {time.time() - now:.2f} sec')
                    else:
                        print(f'{self.W}({self.gettime()}){self.G}[+] Token {token[:24]}.**.*** {self.W}[{self.V}{nitro_type}{self.W}][{self.V}{ev}{self.W}][{self.V}{fv}{self.W}] Time Taken: {time.time() - now:.2f} sec')
                else:
                    print(f'{self.W}({self.gettime()}){self.R}[x] Failed To Save Token In File.')
            elif status == "rate limited":
                self.rate += 1
                save = self.save_into_file('data/to_recheck.txt', token)
                if save:
                    print(f'{self.W}({self.gettime()}){self.Y}[!] Token {token[:24]}.**.*** {self.W} You Are Being Rate Limited. Sleeping for 4 Seconds...')
                    time.sleep(4)
                else:
                    print(f'{self.W}({self.gettime()}){self.R}[x] Failed To Save Token In File.')
                time.sleep(4)
            elif status == "locked":
                self.locked += 1
                save = self.save_into_file('data/locked.txt', token)
                if save:
                    print(f'{self.W}({self.gettime()}){self.G}[+] Token {token[:24]}.**.*** {self.W}Time Taken {time.time() - now:.2f} sec')
                else:
                    print(f'{self.W}({self.gettime()}){self.R}[x] Failed To Save Token In File.')
            elif status == "invalid":
                self.invalids += 1
                save = self.save_into_file('data/invalids.txt', token)
                if save:
                    print(f'{self.W}({self.gettime()}){self.R}[x] Token {token[:24]}.**.*** {self.W}Time Taken {time.time() - now:.2f} sec')
                else:
                    print(f'{self.W}({self.gettime()}){self.R}[x] Failed To Save Token In File.')
        input(f"{self.G}[@] Checker Results: {self.W}{self.valids} {self.G}Valids / {self.W}{self.invalids}{self.G} Invalids / {self.W}{self.locked} {self.G}Locked / {self.W}{self.rate} {self.G}Rate Limited / {self.W}{self.nitro_boost} {self.G}Nitro Boost / {self.W}{self.nitro_classic} {self.G}Nitro Classic")


if __name__ == "__main__":
    checker = TokenChecker()
    checker.main()
