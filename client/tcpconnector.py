from PyQt5.QtNetwork import *

import socket
import game
import ntpath
import os

from protocol import *

BUFFER_SIZE = 1024


class TcpManager:
    def __init__(self):
        pass

    def sendBytes(self, packet, client_socket):
        client_socket.writeData(packet)

    def initPktHeader(self, header_type, size):
        header = PktHeader()
        header.type = header_type
        header.size = size
        return header.encode()

    # SENDING LOGIN
    def sendPktLogin(self, player_name, positions_list_of_tuples, client_socket):
        login = PktLogin()
        login.username = player_name

        if len(positions_list_of_tuples) == login.position_count:
            login.positions = positions_list_of_tuples
            encoded_payload = login.encode()
            packet = self.initPktHeader(PKT_LOGIN_ID, len(encoded_payload)) + encoded_payload

            self.sendBytes(packet, client_socket)
        else:
            print("Number of positions is not equal to position count!")

    # RECEIVING YOUR OWN ID
    def receivePktLoginAck(self, game, packet):

        login_ack = PktLoginAck()

        login_ack.decode(packet)

        game.your_id = login_ack.player_id  # SENDING TO GAME INSTANCE

    # RECEIVING TURN START
    def receivePktTurnStart(self, game, packet):

        turn_start = PktTurnStart()

        turn_start.decode(packet)
        # SENDING TO GAME INSTANCE
        print("turn {} player {}".format(turn_start.turn, turn_start.player_id))
        game.turn = turn_start.turn
        game.whose_turn_player_id = turn_start.player_id

    # SENDING TURN MOVE
    def sendPktTurnMove(self, turn, picked_player_id, position_in_tuple, client_socket):
        turn_move = PktTurnMove()
        turn_move.turn = turn
        turn_move.picked_player_id = picked_player_id
        turn_move.position = position_in_tuple

        encoded_payload = turn_move.encode()
        packet = self.initPktHeader(PKT_TURN_MOVE_ID, len(encoded_payload)) + encoded_payload

        self.sendBytes(packet, client_socket)

    # RECEIVING TURN END
    def receivePktTurnEnd(self, game, packet):

        turn_end = PktTurnEnd()

        turn_end.decode(packet)

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

        game_start.decode(packet)
        # ADDING TO GAME INSTANCE
        game.id = game_start.game_id
        game.players_dictionary = game_start.player_names

    # RECEIVING GAME END
    def receivePktGameEnd(self, game, packet):

        game_end = PktGameEnd()

        game_end.decode(packet)

        if not (game_end.game_id == game.id):
            print("RECEIVED WRONG GAME ID")

        else:
            game.winner_player_id = game_end.winner_player_id

    # RECEIVE MANAGER
    def receivePacket(self, packet, packet_header, game):

        if packet_header == PKT_LOGIN_ACK_ID:
            self.receivePktLoginAck(game, packet)

        elif packet_header == PKT_TURN_START_ID:
            self.receivePktTurnStart(game, packet)

        elif packet_header == PKT_TURN_END_ID:
            self.receivePktTurnEnd(game, packet)

        elif packet_header == PKT_GAME_START_ID:
            self.receivePktGameStart(game, packet)

        elif packet_header == PKT_GAME_END_ID:
            self.receivePktGameEnd(game, packet)

        else:
            print("RECEIVED UNKNOWN PACKET!")

    # TODO: OBSLUGA PLIKU
    def sendPktFileStart(self, filepath, client_socket):
        file_start = PktFileStart()
        file_start.name = ntpath.basename(filepath)
        file_start.size = os.stat(filepath).st_size

        encoded_payload = file_start.encode()
        packet = self.initPktHeader(PKT_FILE_START_ID, len(encoded_payload)) + encoded_payload  # len+8?

        self.sendBytes(packet, client_socket)

    def sendPktFileBlock(self, file_block_2, client_socket):
        file_block = PktFileBlock()
        file_block.block = file_block_2

        encoded_payload = file_block.encode()
        packet = self.initPktHeader(PKT_FILE_BLOCK_ID, len(encoded_payload)) + encoded_payload  # len+8?

        self.sendBytes(packet, client_socket)

