#!/usr/bin/env python3
import select
import socket
import random
import com
import os

# ToDO: Who just shuffled can't draw cards

message_present = "{} von {} Spieler*innen anwesend."
message_waiting = "Warte auf Spieler*innen."
message_start = "Spiel wird gestartet."
players = 1

draw_pile = []
open_dis = []
cov_dis = []
players_piles = []
msg = None
cards_given = False

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 1338))
server.listen(5)

inpt = [server]
names = ["server"]
disconnected = 0


def name_player(val, sock, names):
    if len(val) > 1:
        val.replace("|", "I")
        ind = int(val[0])
        val = val[1:]
        while val in names:
            if isinstance(value[-1], int):
                val = val[:-1] + str(int(val[-1])+1)
            else:
                val += " " + str(names.count(val) + 1)
        try:
            names[ind] = val
        except IndexError:
            names.append(val)
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


def discard(pile, value, sock):
    pile.append(value)
    players_piles[inpt.index(sock)-1].remove(value)


def work_sockets(msg, sock):
    global draw_pile
    global cov_dis
    global open_dis
    global players_piles
    global cards_given
    tag, value, msg, player = com.read_message(msg)
    while True:
        if tag == com.tag_no_msg:
            break
        elif tag == com.tag_socket_closed:
            print("Verbindung zu client verloren.")
            close_connection(sock)
        elif tag == com.tag_give_cards:
            if players_piles[player-1] is None:
                players_piles[player-1] = [value]
            else:
                players_piles[player-1].append(value)
        elif tag == com.tag_draw_pile:
            draw_pile.append(value)
        elif tag == com.tag_open_dis:
            discard(open_dis, value, sock)
            send_players(inpt, com.write_message(com.tag_open_dis, value, player))
        elif tag == com.tag_cov_dis:
            discard(cov_dis, value, sock)
        elif tag == com.tag_shuffle:
            if value == "open":
                if len(open_dis) > 0:
                    print(type(open_dis), open_dis)
                    print(type(draw_pile))
                    random.shuffle(open_dis)
                    draw_pile += open_dis
                    open_dis = []
                    send_players(inpt, com.write_message(com.tag_empty_dp, str(1)))
            elif value == "cov":
                if len(cov_dis) > 0:
                    random.shuffle(cov_dis)
                    draw_pile.append(cov_dis)
                    cov_dis = []
                    send_players(inpt, com.write_message(com.tag_empty_dp, str(1)))
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
        # else:
        #     communication.send_message(sock, communication.write_message(0, "Error client: Tag " + str(tag) + "unknown."))
        if msg is None:
            return msg
        else:
            tag, value, msg, player = com.read_message(msg)


def end_game():
    for sock in inpt[1:]:
        sock.close()
    quit()


def close_connection(sock):
    index = inpt.index(sock)
    # Make potential newly arrived client the last one
    players_piles.append(players_piles[index-1])
    players_piles.pop(index-1)

    inpt.pop(index)
    sock.close()
    send_players(inpt, com.write_message(com.tag_socket_closed, names[index]))
    if index == 1:
        send_players(inpt, com.write_message(com.tag_end, "Dealer left"))
        end_game()
    names.pop(index)


while 1:
    try:
        if msg is not None:
            buf = msg
        else:
            buf = 2
            inputready, outputready, exceptready = select.select(inpt, [], [])
            for s in inputready:
                if s == server:
                    if len(inpt) <= players:
                        client, addr = server.accept()
                        tag, value, msg, player, sock = com.receiving([client])
                        if len(inpt) == 1 and player or len(inpt) > 1 and not player:
                            inpt.append(client)
                            names.append(value)
                            if player:
                                players = player
                                players_piles = [None] * players
                        else:
                            if player:
                                com.send_message(client, com.write_message(com.tag_yet_to_start, "Hier ist schon ein "
                                                 "Dealer. Nimm als Client teil oder such dir nen eigenen Server!"))
                            else:
                                com.send_message(client, com.write_message(com.tag_yet_to_start,
                                                                           "Spiel noch nicht gestartet."))
                                client.close()
                        if len(inpt) == players + 1:
                            for i, s in enumerate(inpt[1:]):
                                com.send_message(s, com.write_message(com.tag_index, str(i + 1)))
                            send_players(inpt, com.write_message(com.tag_start, com.encode_list(names[1:])))
                            if cards_given:
                                for pile in players_piles[-disconnected:]:
                                    for card in pile:
                                        com.send_message(inpt[-disconnected], com.write_message(com.tag_take_cards, card))
                                    disconnected -= 1
                            else:
                                for index, pile in enumerate(players_piles):
                                    for card in pile:
                                        com.send_message(inpt[index + 1], com.write_message(com.tag_take_cards, card))
                                cards_given = True
                else:
                    buf, s = com.receive_message([s])
                    if not buf:
                        disconnected += 1
                        close_connection(s)
        if buf and buf != 2:
            msg = work_sockets(buf, s)
    except ConnectionError:
        for sock in inpt[1:]:
            try:
                com.send_message(sock, com.write_message(com.tag_check_connection, "Checking connection"))
            except ConnectionError:
                disconnected += 1
                close_connection(sock)
