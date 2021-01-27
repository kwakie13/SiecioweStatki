#define POSITION_COUNT 5
#define MAX_PACKET_SIZE 2100000
#define PLAYER_COUNT 4
#define SERVER_PORT 3124
HEADER_SIZE = 8

PKT_LOGIN_ID = 1
PKT_LOGIN_ACK_ID = 2
PKT_TURN_START_ID = 3
PKT_TURN_MOVE_ID = 4
PKT_TURN_END_ID = 5
PKT_GAME_START_ID = 6
PKT_GAME_END_ID = 7
PKT_FILE_START_ID = 8
PKT_FILE_BLOCK_ID = 9

#FUNKCJE DEKODUJACE/ENKODUJACE
def decode_string(bytes):
    size = int.from_bytes(bytes[0:4], 'big')
    string_bytes = bytes[4:4+size]
    string = string_bytes.decode('utf-8')

    return (string, 4 + size)

def encode_string(string):
    encoded = string.encode()
    string_length = len(encoded)
    return string_length.to_bytes(4,'big') + encoded



def decode_position(bytes):
    x = int.from_bytes(bytes[0:1], 'big')
    y = int.from_bytes(bytes[1:2], 'big')

    return ((x, y), 2)

def encode_position(x, y):
    
    return x.to_bytes(1, 'big') + y.to_bytes(1, 'big')




#NAGŁOWEK

class PktHeader:
    def __init__(self):
        self.type = 0
        self.size = 0

    def decode(self, bytes):
        self.type = int.from_bytes(bytes[0:4], 'big')
        self.size = int.from_bytes(bytes[4:9], 'big')

    def encode(self):
        enctype = self.type.to_bytes(4, 'big')
        encsize = self.size.to_bytes(4, 'big')
        return enctype + encsize




#LOGOWANIE

class PktLogin:
    def __init__(self):
        self.username = ''
        self.position_count = 20
        self.positions = self.position_count * [(0, 0)] #POSITION COUNT 20
        

    def decode(self, bytes):
        username, read_bytes = decode_string(bytes)
        
        self.username = username
        self.positions = []

        for i in range(self.position_count): #POSITION COUNT 20
            position, read_bytes2 = decode_position(bytes[read_bytes:])
            read_bytes += read_bytes2
            self.positions.append(position)

    def encode(self):
        bytes = b''
        bytes = bytes + encode_string(self.username)

        for i in range(self.position_count): #POSITION COUNT 20
            bytes = bytes + encode_position(self.positions[i][0], self.positions[i][1])

        return bytes



class PktLoginAck:
    def __init__(self):
        self.player_id = 0

    def decode(self, bytes):
        self.player_id = int.from_bytes(bytes[0:1], 'big')


#TURY

class PktTurnStart:
    def __init__(self):
        self.turn = 0
        self.player_id = 0
    
    def decode(self, bytes):
        self.turn = int.from_bytes(bytes[0:4], 'big')
        self.player_id = int.from_bytes(bytes[4:], 'big')



class PktTurnMove:
    def __init__(self):
        self.turn = 0
        self.picked_player_id = 0
        self.position = (0,0)

    def encode(self):
        return self.turn.to_bytes(4, 'big') + self.picked_player_id.to_bytes(1, 'big') + encode_position(self.position[0], self.position[1])


class PktTurnEnd:
    def __init__(self):
        self.turn = 0
        self.player_id = 0
        self.picked_player_id = 0
        self.position = ((0,0),2)
        self.success = 0
    
    def decode(self, bytes):
        self.turn = int.from_bytes(bytes[0:4], 'big')
        self.player_id = int.from_bytes(bytes[4:5], 'big')
        self.picked_player_id = int.from_bytes(bytes[5:6], 'big')
        self.position = decode_position(bytes[6:8])
        self.success = int.from_bytes(bytes[8:], 'big')

#GRA

class PktGameStart:
    def __init__(self):
        self.game_id = 0
        self.player_names = {}

    def decode(self, bytes):
        self.game_id = int.from_bytes(bytes[0:4], 'big')
        read_bytes = 4
        for i in range(4):
            decoded = decode_string(bytes[read_bytes:])
            name = decoded[0]
            read_bytes2 = decoded[1]
            read_bytes += read_bytes2
            self.player_names[i + 1] = name


class PktGameEnd:
    def __init__(self):
        self.game_id = 0
        self.winner_player_id = 0

    def decode(self, bytes):
        self.game_id = int.from_bytes(bytes[0:4], 'big')
        self.winner_player_id = int.from_bytes(bytes[4:5], 'big')



#TRANSFER PLIKÓW NA SERWER

class PktFileStart:
    def __init__(self):
        self.name = ''
        self.size = 0

    def encode(self):
        return encode_string(self.name) + self.size.to_bytes(4, 'big')


class PktFileBlock:
    def __init__(self):
        self.block = ''

    def encode(self):
        #return encode_string(self.block)
        return str.encode(self.block)



