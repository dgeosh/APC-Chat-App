import websocket
import threading
import os

room = input("Room code: ")
name = input("Your name: ")
os.system('cls' if os.name=='nt' else 'clear')
print("New message: ",end="",flush=True)

WEBSOCKET_ENDPOINT = "YOUR-URL-HERE"
ws = websocket.WebSocket()
ws.connect(WEBSOCKET_ENDPOINT, subprotocols=[room])

def getch_getter():
    try:
        import termios
    except ImportError:
        # not posix. return windows msvcrt getch
        import msvcrt
        return msvcrt.getch
    # yes posix. fake getch using tty
    import sys, tty
    def fake_getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    return fake_getch

getch = getch_getter()

def cursor_at_start():
    buf = ""
    print("\x1b[6n",end="",flush=True)  # ANSI code for cursor position request
    
    while True:
        char = getch()
        try:
            char = char.encode().decode()
        except:
            char = char.decode()
        buf += char
        if char == "R":
            break

    # detect horiziontal cursor position
    try:
        _, pos = buf.split("[")[1].split("R")[0].split(";")
        return (int(pos) == 1)
    except:
        return False

def get_messages():
    global sent_message
    while True:
        word = ws.recv()
        erase_len = len(word) + 13
        erased = os.get_terminal_size().columns
        print("\033[2K", end="",flush=True)
        while(erased < erase_len):
            print("\033[F\033[2K",end="",flush=True)
            erased += os.get_terminal_size().columns
        print("\033[2K", end="", flush=True)
        print(f"\r{word}", flush=True)
        print(f"\rNew message: {''.join(current_message)}",end="",flush=True)
        
        sent_message = False

current_message = []

def send_messages():
    global sent_message
    global current_message
    while True:
        ch = getch()
        if ch == b'\r' or ch == '\r':
            if len(current_message) > 0:
                ws.send(f"{name}: {''.join(current_message)}")
                current_message = []
        elif ch == b'\x08' or ch == '\x7f':
            if len(current_message) > 0:
                if(cursor_at_start()):
                    print("\033[F",end="", flush=True)
                    print("\033["+str(os.get_terminal_size().columns+1)+"C ",end="",flush=True)
                else:
                    print("\b \b",end="", flush=True)
                current_message.pop()
        else:
            try:
                current_message.append(ch.decode())
                print(ch.decode(), end="", flush=True)
            except:
                current_message.append(ch)
                print(ch, end="", flush=True)

threading.Thread(target=get_messages).start()
threading.Thread(target=send_messages).start()