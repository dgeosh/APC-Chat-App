import asyncio

from websockets.asyncio.server import serve

rooms = {}

async def handle(websocket):
    while True:
        try:
            if(websocket.subprotocol == None):
                await websocket.close(1002, "No Subprotocol Specified")
                return
            message = await websocket.recv()
            if websocket.subprotocol in rooms.keys():
                for conn in rooms[websocket.subprotocol]:
                    try:
                        await conn.send(message)
                    except:
                        pass
        except:
            if websocket.subprotocol in rooms.keys():
                print(rooms)
                rooms[websocket.subprotocol].remove(websocket)
                print(rooms)
                if rooms[websocket.subprotocol] == []:
                    rooms.pop(websocket.subprotocol)
                print(rooms)
            return

def protocol_selector(conn, protocols):
    if(len(protocols) > 0):
        if not protocols[0] in rooms.keys():
            print("Creating new Room for", protocols[0])
            rooms[protocols[0]] = []
        rooms[protocols[0]].append(conn)
        print("Adding new client to room",protocols[0])
        return protocols[0]
    else:
        return None

async def main():
    server = await serve(handle, "localhost", 5678, select_subprotocol=protocol_selector, server_header=None, )
    await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
