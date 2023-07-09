import datetime


class Logger:
    def __init__(self) -> None:
        self.light_black = "\x1b[90m"
        self.reset = "\x1b[39m"
        self.white = "\x1b[37m"

    def info(self, message: str):
        time = datetime.datetime.now().strftime(f"%H:%M:%S")
        print(f'{self.light_black}[{self.white}{time}{self.light_black}] {self.reset}{message}')

    def inpt(self, message: str):
        time = datetime.datetime.now().strftime(f"%H:%M:%S")
        inp = input(f'{self.light_black}[{self.white}{time}{self.light_black}] {self.reset}{message}')
        return inp