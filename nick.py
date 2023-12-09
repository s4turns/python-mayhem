import socket
import random
import string
import time

class IRCBot:
    def __init__(self, server, port, channel, channel_key, default_nickname):
        self.server = server
        self.port = port
        self.channel = channel
        self.channel_key = channel_key
        self.default_nickname = default_nickname

    def connect(self):
        self.socket = socket.socket()
        self.socket.connect((self.server, self.port))

        # Add a random character to the default nickname
        random_char = self.generate_random_symbol()
        self.default_nickname += random_char

        # Ensure the default nickname is unique
        while not self.is_nickname_available(self.default_nickname):
            random_char = self.generate_random_symbol()
            self.default_nickname = self.default_nickname[:-1] + random_char

        self.send("NICK {}".format(self.default_nickname))
        self.send("USER {} 0 * :{}".format(self.default_nickname, self.default_nickname))
        self.join_channel()

    def is_nickname_available(self, nickname):
        self.send("NICK {}".format(nickname))
        time.sleep(1)  # Add a delay to give the server time to process the NICK command
        data = self.socket.recv(2048).decode("utf-8")
        return "433" not in data

    def join_channel(self):
        if self.channel_key:
            self.send("JOIN {} {}".format(self.channel, self.channel_key))
        else:
            self.send("JOIN {}".format(self.channel))

    def send(self, message):
        self.socket.send("{}\r\n".format(message).encode("utf-8"))

    def change_nickname(self, new_nickname):
        while not self.is_nickname_available(new_nickname):
            if len(new_nickname) > 9:
                new_nickname = new_nickname[:9] + self.generate_random_symbol()

            self.send("NICK {}".format(new_nickname))
            time.sleep(1)  # Add a delay to give the server time to process the NICK command

    def generate_random_symbol(self):
        symbols = string.ascii_letters + string.digits
        return random.choice(symbols)

    def listen(self):
        while True:
            data = self.socket.recv(2048).decode("utf-8")
            print(data)

            if "PING" in data:
                self.send("PONG {}".format(data.split()[1]))

            # Handle other IRC events or commands as needed
            if "PRIVMSG" in data and self.channel in data and "!nick" in data:
                sender = data.split('!')[0][1:]
                parts = data.split('PRIVMSG {} :'.format(self.channel))
                message = parts[1].strip()
                if message.startswith("!nick"):
                    new_nickname = message.split()[1]
                    self.change_nickname(new_nickname)

if __name__ == "__main__":

    server = "irc.servercentral.net"
    port = 6667
    channel = ""
    channel_key = ""
    default_nickname = ""

    bot = IRCBot(server, port, channel, channel_key, default_nickname)
    bot.connect()
    bot.listen()
