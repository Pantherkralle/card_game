#!/usr/bin/env python3
import select
import socket
import random
import com


message_present = "{} von {} Spieler*innen anwesend."
message_waiting = "Warte auf Spieler*innen."
message_start = "Spiel wird gestartet."
players = 1

draw_pile = []
open_dis = []
cov_dis = []
players_piles = []
msg = None

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 1338))
server.listen(5)

inpt = [server]
names = ["server"]


def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def name_player(val, sock, names):
    if len(val) > 1:
        val.replace("|", "I")
        ind = int(val[0])
        val = val[1:]
        while val in names:
            if is_int(value[-1]):
                val = val[:-1] + str(int(val[-1])+1)
            else:
                val += " " + str(names.count(val) + 1)
        names[ind] = val
    return names


def send_players(sockets, message):
    """
    Sends a string to each client connected to (each socket object except for the first one).

    Parameters
    ----------
    sockets: list
        list of all socket objects connected to
        first element is listening socket (server)
        other elements are connection sockets (clients).
    message: bytes
        Message to be send to clients.
    """
    for s in sockets[1:]:
        com.send_message(s, message)


def work_sockets(msg):
    global draw_pile
    global cov_dis
    global open_dis
    global players_piles
    tag, value, msg, player = com.read_message(msg)
    while True:
        if tag == com.tag_no_msg:
            break
        elif tag == com.tag_socket_closed:
            print("Verbindung zu client verloren.")
        if tag == com.tag_players:
            global players
            global names
            players = int(value)
            num = 2
            while len(names) < players + 1:
                names.append("player " + str(num))
                num += 1
            players_piles = [None] * players
            print("received players:", players_piles)
        elif tag == com.tag_piles_size:
            piles_size = int(value)
        elif tag == com.tag_give_cards:
            print("tag_give_cards:", players_piles)
            if players_piles[player-1] is None:
                players_piles[player-1] = [value]
            else:
                players_piles[player-1].append(value)
            com.send_message(inpt[player], com.write_message(com.tag_take_cards, value))
        elif tag == com.tag_draw_pile:
            draw_pile.append(value)
        elif tag == com.tag_open_dis:
            open_dis.append(value)
            print("Moin")
            send_players(inpt, com.write_message(com.tag_open_dis, value, player))
        elif tag == com.tag_cov_dis:
            cov_dis.append(value)
        elif tag == com.tag_shuffle:
            if value == "open":
                print("draw_pile before shuffling:", draw_pile)
                if len(open_dis) > 0:
                    draw_pile += random.shuffle(open_dis)
                    open_dis = []
                    send_players(inpt, com.write_message(com.tag_empty_dp, str(1)))
                print("draw_pile after shuffling:", draw_pile)
                print("shuffle open discard pile")
            elif value == "cov":
                print("draw_pile before shuffling:", draw_pile)
                if len(cov_dis) > 0:
                    draw_pile += random.shuffle(cov_dis)
                    cov_dis = []
                    send_players(inpt, com.write_message(com.tag_empty_dp, str(1)))
                print("draw_pile after shuffling:", draw_pile)
                print("shuffle covered discard pile")
        elif tag == com.tag_draw:
            if len(draw_pile) > 0:
                com.send_message(inpt[player], com.write_message(com.tag_take_cards, draw_pile[0]))
                if players_piles[player-1] == None:
                    players_piles[player-1] = [value]
                else:
                    players_piles[player-1].append(draw_pile[0])
                draw_pile.pop(0)
            if len(draw_pile) == 0:
                send_players(inpt, com.write_message(com.tag_empty_dp, str(0)))
        elif tag == com.tag_usernames:
            # global names
            names = name_player(value, sock, names)
            send_players(inpt, com.write_message(com.tag_usernames, com.encode_list(names[1:])))
            # return names
        # else:
        #     communication.send_message(sock, communication.write_message(0, "Error client: Tag " + str(tag) + "unknown."))
        if msg is None:
            return msg
        else:
            tag, value, msg, player = com.read_message(msg)


while 1:
    if msg is not None:
        buf = msg
    else:
        buf = 2
        inputready, outputready, exceptready = select.select(inpt, [], [])
        for s in inputready:
            if s == server:
                if len(inpt) <= players:
                    client, addr = server.accept()
                    if len(inpt) == 1:
                        tag, value, msg, player, sock = com.receiving([client])
                        print("Tag:", tag, "value:", value)
# ToDo: Wenn Verbindung vor Name Input geschlossen wird, funktioniert es nicht. try - except?
                        if tag == com.tag_prior_user and value == "secret_message":
                            inpt.append(client)
                            names.append("player 1")
                        else:
                            com.send_message(client, com.write_message(com.tag_yet_to_start, "Spiel noch nicht gestartet."))
                            client.close()
                            # print("connected to other player: connection closed")
                            # print("len(inpt):", len(inpt))
                            # print("inpt:", inpt)
                    else:
                        inpt.append(client)
                        message = message_present.format((len(inpt) - 1), players)
                        com.send_message(client, com.write_message(com.tag_index, str(inpt.index(client))))
                        send_players(inpt, com.write_message(com.tag_notification, message))
                        send_players(inpt, com.write_message(com.tag_players, str(players)))
                        send_players(inpt, com.write_message(com.tag_usernames, com.encode_list(names[1:])))
                        if len(inpt) <= players:
                            send_players(inpt, com.write_message(com.tag_notification, message_waiting))
                        else:
                            send_players(inpt, com.write_message(com.tag_start, message_start))
                            # send_players(inpt, com.write_message(com.tag_usernames, com.encode_list(names[1:])))
            else:
                buf, s = com.receive_message([s])
                if not buf:
                    inpt.pop(inpt.index(s))
                    s.close()
    if buf and buf != 2:
        msg = work_sockets(buf)

    print("players piles:", players_piles)
