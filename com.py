#!/usr/bin/env python3
import select
import socket

# tags
tag_error = 0
tag_error_tag = 1
tag_socket_closed = 2
tag_no_msg = 3
tag_yet_to_start = 4
tag_check_connection = 5
tag_usernames = 10
tag_prior_user = 11
tag_index = 12
tag_notification = 20
tag_start = 21
tag_end = 22
tag_cards_given = 23
tag_give_cards = 30
tag_draw_pile = 31
tag_take_cards = 32
tag_empty_dp = 33
tag_draw = 34
tag_open_dis = 35
tag_cov_dis = 36
tag_shuffle = 37
tag_players = 40
tag_piles_size = 41
tags_to_all = [tag_notification, tag_start]
tags_specific_player = [tag_give_cards, tag_draw, tag_open_dis, tag_cov_dis]

timeout = 0.01

def encode_list(list):
    string = ""
    for i in list[:-1]:
        string += i + "|"
    string += list[-1]
    return string


def send_message(sock, message):
    """
    Sending function.

    Parameters
    ----------
    sock: socket object
        Connection to addressee
    message: bytes
        Message to be sent.
    """
    success = False

    while not success:
        inputready, outputready, exceptready = select.select([], [sock], [], timeout)
        if sock in outputready:
            sock.sendall(message)
            # print("fcn send_message. sent message:", message)
            success = True
        else:
            success = False
            # print("fcn send_message. tried to send message", read_message(message))


def write_message(tag, value, player=None):
    msg = b""
    msg += tag.to_bytes(1, "big")
    value = value.encode('utf-8')
    msg += len(value).to_bytes(1, "big")
    if tag in tags_specific_player:
        msg += player.to_bytes(1, "big")
    msg += value
    return msg


def receiving(sockets):
    msg, sock = receive_message(sockets)
    if msg == 2:
        return tag_no_msg, None, None, None, sock
    if not msg:
        print("Where are you?")
        sock.close()
        return tag_socket_closed, None, None, None, sock
    tag, value, msg, player = read_message(msg)
    return tag, value, msg, player, sock


def receive_message(sockets):
    inputready, outputready, exceptready = select.select(sockets, [], [], timeout)
    received = b""
    if len(inputready) == 0:
        return 2, 0
    while len(inputready) > 0:
        for sock in inputready:                                                       # Was, wenn mehrere sockets ready?
            buf = sock.recv(1024)
            # print("fcn receive_message. just received", buf)
            received += buf
            if buf == b"":
                if received == b"":
                    received = None
                # print("fcn receive_message. received in total =", received)
                return received, sock
            inputready, outputready, exceptready = select.select(sockets, [], [], timeout)
    return received, sock


def read_message(msg):
    # print("fcn read_message. reading", msg)
    if len(msg) < 3:
        # print("fcn read_message. message incomplete")
        return tag_no_msg, 0, None, None
    tag = int(msg[0])
    # print("fcn read_message. Tag read:", tag)
    len_recv = int(msg[1])
    # print("fcn read_message. length read:", len_recv)
    if tag in tags_specific_player:
        player = int(msg[2])
        len_meas = len(msg[3:])
        shifter = 1
    else:
        player = None
        shifter = 0
        len_meas = len(msg[2:])
    if len_recv <= len_meas:
        value = msg[2+shifter:(2+shifter+len_recv)].decode('utf-8')
        # print("fcn read_message. received complete message:", value)
        wait = False
        if len_recv < len_meas:
            msg = msg[2+shifter+len_recv:]
            # print("fcn read_message. still to read:", msg)
        else:
            # print("fcn read_message. read all")
            msg = None
    else:
        # print("fcn read_message. received incomplete message:", msg)
        value = None
        msg = msg
        player = None
        wait = True
    if msg == b"":
        # print("fcn read_message. setting empty message to None")
        msg = None
    # print(tag, value)
    # print(msg)
    # print(player)
    print("tag =", tag, ", value =", value, "player =", player)
    return tag, value, msg, player


def decode_list(string):
    return string.split("|")


def give_cards(inpt, players, players_piles):
    i = 1
    while i <= players:
        s = inpt[i]
        for c in players_piles[i-1]:
            send_message(s, write_message(tag_give_cards, c, i))
        i = i + 1
