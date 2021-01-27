import ntpath
import os
import socket

from protocol import *

BUFFER_SIZE = 1024


class TcpManager:
    def __init__(self):
        self.host = '10.50.140.221'
        self.port = 3124
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def close(self):
        self.client_socket.close()

    def sendBytes(self, packet):
        self.client_socket.send(packet)

    def initPktHeader(self, header_type, size):  # size+8?
        header = PktHeader()
        header.type = header_type
        header.size = size
        return header.encode()

    # SENDING LOGIN
    def sendPktLogin(self, player_name, positions_list_of_tuples):
        login = PktLogin()
        login.username = player_name

        if len(positions_list_of_tuples) == login.position_count:
            login.positions = positions_list_of_tuples
            encoded_payload = login.encode()
            packet = self.initPktHeader(PKT_LOGIN_ID, len(encoded_payload)) + encoded_payload  # len+8?
            self.client_socket.send(packet)
        else:
            print("Number of positions is not equal to position count!")

    # RECEIVING YOUR OWN ID
    def receivePktLoginAck(self, game, packet):

        login_ack = PktLoginAck()
        login_ack.decode(packet[HEADER_SIZE:])

        game.your_id = login_ack.player_id  # SENDING TO GAME INSTANCE

    # RECEIVING TURN START
    def receivePktTurnStart(self, game, packet):

        turn_start = PktTurnStart()
        turn_start.decode(packet[HEADER_SIZE:])
        # SENDING TO GAME INSTANCE
        game.turn = turn_start.turn
        game.whose_turn_player_id = turn_start.player_id

    # SENDING TURN MOVE
    def sendPktTurnMove(self, turn, picked_player_id, position_in_tuple):
        turn_move = PktTurnMove()
        turn_move.turn = turn
        turn_move.picked_player_id = picked_player_id
        turn_move.position = position_in_tuple

        encoded_payload = turn_move.encode()
        packet = self.initPktHeader(PKT_TURN_MOVE_ID, len(encoded_payload)) + encoded_payload  # len+8?
        self.client_socket.send(packet)

    # RECEIVING TURN END
    def receivePktTurnEnd(self, game, packet):

        turn_end = PktTurnEnd()
        turn_end.decode(packet[HEADER_SIZE:])

        if not (turn_end.turn == game.turn):
            print("PROBLEM WITH TURN SYNCHRONIZATION (WRONG TURN NUMBER)")

        elif not (turn_end.player_id == game.whose_turn_player_id):
            print("PROBLEM WITH TURN SYNCHRONIZATION (WRONG ATTACKING PLAYER ID)")

        else:  # ADDING TO GAME INSTANCE
            game.attacked_player = turn_end.picked_player_id
            game.position_attacked = turn_end.position
            game.success_of_attack = turn_end.success

    # RECEIVING GAME START
    def receivePktGameStart(self, game, packet):

        game_start = PktGameStart()
        game_start.decode(packet[HEADER_SIZE:])
        # ADDING TO GAME INSTANCE
        game.id = game_start.game_id
        game.players_dictionary = game_start.player_names

    # RECEIVING GAME END
    def receivePktGameEnd(self, game, packet):

        game_end = PktGameEnd()
        game_end.decode(packet[HEADER_SIZE:])

        if not (game_end.game_id == game.id):
            print("RECEIVED WRONG GAME ID")

        else:
            game.winner_player_id = game_end.winner_player_id

    # RECEIVE MANAGER
    def receivePacket(self, game):
        packet = self.client_socket.recv(8)
        header = PktHeader()
        header.decode(packet)
        packet += self.client_socket.recv(header.size)
        print(header.type)

        if header.type == PKT_LOGIN_ACK_ID:
            self.receivePktLoginAck(game, packet)

        elif header.type == PKT_TURN_START_ID:
            self.receivePktTurnStart(game, packet)

        elif header.type == PKT_TURN_END_ID:
            self.receivePktTurnEnd(game, packet)

        elif header.type == PKT_GAME_START_ID:
            self.receivePktGameStart(game, packet)

        elif header.type == PKT_GAME_END_ID:
            self.receivePktGameEnd(game, packet)

        else:
            print("RECEIVED UNKNOWN PACKET!")

    # TODO: OBSLUGA PLIKU
    def sendPktFileStart(self, filepath):
        file_start = PktFileStart()
        file_start.name = ntpath.basename(filepath)
        file_start.size = os.stat(filepath).st_size

        encoded_payload = file_start.encode()
        packet = self.initPktHeader(PKT_FILE_START_ID, len(encoded_payload)) + encoded_payload  # len+8?
        self.client_socket.send(packet)

    def sendPktFileBlock(self, file_block):
        file_block = PktFileBlock()
        file_block.block = file_block

        encoded_payload = file_block.encode()
        packet = self.initPktHeader(PKT_FILE_BLOCK_ID, len(encoded_payload)) + encoded_payload  # len+8?
        self.client_socket.send(packet)
