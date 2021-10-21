

    while (True):
        prev_turn = game_data.turn

        tcp_manager.receivePacket(game_data)  # WAITING FOR NEW TURN

        if game_data.turn == prev_turn:
            print("NIE MOZE ZACZAC TURY :(")
            continue

        elif game_data.whose_turn_player_id == game_data.your_id:  # TY DOSTAJESZ TURE

            while (True):
                w_kogo = input("W kogo chcesz strzelic (id): ")
                w_kogo = int(w_kogo)
                x = input("X: ")
                x = int(x)
                y = input("Y: ")
                y = int(y)

                if (ilosc_zatopionych[w_kogo] < 20) and (w_kogo in [1, 2, 3, 4]):
                    break

                elif w_kogo == game_data.your_id:
                    print("nie mozesz strzelic sam w siebie")

                else:
                    print("ten gracz juz nie zyje")

            tcp_manager.sendPktTurnMove(game_data.turn, w_kogo, (x, y))  # WYSYLAMY NASZ RUCH

        tcp_manager.receivePacket(game_data)  # WAITING FOR TURN END OR GAME END

        if game_data.winner_player_id == 0:  # GRA JESZCZE NIE JEST SKONCZONA
            # SPRAWDZAMY CZY TRAFIONO, JESLI TAK DODAJEMY +1 DO SLOWNIKA
            if game_data.success_of_attack == 1:
                ilosc_zatopionych[game_data.attacked_player] += 1

            continue

        elif game_data.winner_player_id == game_data.your_id:  # TY WYGRALES, PRZESYLASZ PLIK
            # TODO: wybieramy plik, przekazujemy jego fullpath do funkcji ktora przesyla go na serwer
            full_path = 'H:\\OBS\\WIDEO\\wideo01pracprog.mkv'
            leftData = os.stat(full_path).st_size

            tcp_manager.sendPktFileStart(full_path)

            with open(full_path, "rb") as opened_file:

                while (leftData > FILE_BLOCK_SIZE):
                    tcp_manager.sendPktFileBlock(opened_file.read(FILE_BLOCK_SIZE))
                    leftData = leftData - FILE_BLOCK_SIZE

                if leftData > 0:
                    tcp_manager.sendPktFileBlock(opened_file.read(leftData))

            break

        else:  # GRA SIE SKONCZYLA ALE NIE WYGRALES
            # zamykamy okno
            tcp_manager.close()
            print("koniec gry")
            break
