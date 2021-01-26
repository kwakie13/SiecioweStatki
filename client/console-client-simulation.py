import tcp-connector
import game

#[(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]

username = "Szymon"
positions = [(1,1), (1,2), (1, 3), (1, 4), (3, 2), (3, 3), (3, 4), (5, 2), (5, 3), (5, 4), (1, 7), (1, 8), (3, 7), (3, 8), (5, 7), (5, 8), (7, 10), (8, 6), (9, 4), (10, 2)]

ilosc_zatopionych = {1: 0, 2: 0, 3: 0, 4: 0}

tcp_manager = TcpManager() #INICJUJEMY POLACZENIE
tcp_manager.sendPktLogin(username, positions) #WYSYLAMY NASZ LOGIN

game_data = Game() #INICJUJEMY GRE

tcp_manager.receivePacket(game_data)  # WAITING FOR ACK LOGIN

tcp_manager.receivePacket(game_data)  # WAITING FOR GAME START

if ((game_data.your_id != 0 ) and (game_data.id != 0)):
    print("twoje id: " + str(game_data.your_id))


    while(True):
        prev_turn = game_data.turn

        tcp_manager.receivePacket(game_data) # WAITING FOR NEW TURN

        if game_data.turn == prev_turn: 
            print("NIE MOZE ZACZAC TURY :(")
            continue

        elif game_data.whose_turn_player_id == game_data.your_id: #TY DOSTAJESZ TURE
            
            while(True):
                w_kogo = input("W kogo chcesz strzelic (id): ")
                x = input("X: ")
                y = input("Y: ")

                if ilosc_zatopionych[w_kogo] < 20:
                    break

                elif w_kogo = game_data.your_id:
                    print("nie mozesz strzelic sam w siebie")

                else:
                    print("ten gracz juz nie zyje")

            tcp_manager.sendPktTurnMove(game_data.turn, w_kogo, (x, y)) # WYSYLAMY NASZ RUCH


        tcp_manager.receivePacket(game_data) # WAITING FOR TURN END OR GAME END

        if game_data.winner_player_id == 0: # GRA JESZCZE NIE JEST SKONCZONA
            # SPRAWDZAMY CZY TRAFIONO, JESLI TAK DODAJEMY +1 DO SLOWNIKA
            if game_data.success_of_attack == 1:
                ilosc_zatopionych[game_data.attacked_player] += 1

            continue


        elif game_data.winner_player_id == game_data.your_id: #TY WYGRALES, PRZESYLASZ PLIK
            #TODO: wybieramy plik, przekazujemy jego fullpath do funkcji ktora przesyla go na serwer
            break
            

        else: # GRA SIE SKONCZYLA ALE NIE WYGRALES
            #zamykamy okno
            tcp_manager.close()
            print("koniec gry")
            break

        
        
        
