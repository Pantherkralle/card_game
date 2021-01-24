import GUI
import pygame
from pygame.locals import *
import socket
import sys
import com


addr = "127.0.0.1"
port = 1338
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

pygame.init()  # initialize pygame
fps = 30
clock = pygame.time.Clock()

index_big_card = - 1
card_pos_y = GUI.card_pos_y
distance = GUI.distance

pers_ind = None
draw = []
msg = None
name = None
draw_pile = True


def personalize(listed, per_ind):
    pers_list = listed[pers_ind - 1:]
    for element in listed[:per_ind - 1]:
        pers_list.append(element)
    return pers_list


def work_sockets(sockets):
    try:
        tag, value, rest, player, sock = com.receiving(sockets)
    except ValueError:
        pygame.quit()
        sys.exit()
    while True:
        if tag == com.tag_end:
            sockets[0].close()
        elif tag == com.tag_no_msg:
            break
        elif tag == com.tag_open_dis:
            GUI.open_discard_pile.value = value
        elif tag == com.tag_empty_dp:
            global draw_pile
            draw_pile = int(value)
        elif tag == com.tag_socket_closed:
            GUI.show_comment("Verbindung zum Server verloren.", GUI.par.center, 500)
        elif tag == com.tag_index:
            global pers_ind
            pers_ind = int(value)
            # print("Pers_ind:", pers_ind)
        elif tag in [com.tag_yet_to_start, com.tag_socket_closed]:
            note = GUI.Comment("Verbindung zum Server konnte nicht hergestellt werden, da Spiel noch nicht gestartet "
                               "oder bereits alle Spielenden anwesend.")
            note.show()
            pygame.display.update()
            clock.tick(1/5)
            pygame.quit()
            quit()
        elif tag == com.tag_players:
            GUI.par.other_players = int(value) - 1
            GUI.par.set(GUI.par.other_players, 250 // GUI.par.other_players)
            GUI.par.name(GUI.names_default(GUI.par.other_players))
        elif tag in com.tags_to_all:
            GUI.show_comment(value, GUI.par.center, 200)
            # print(value)
        elif tag == com.tag_take_cards:
            GUI.hand.append(value)
            # print("received  card")
        elif tag == com.tag_usernames:
            listed = com.decode_list(value)
            GUI.par.name(listed)
            # print("names unordered:", listed)
            # print("names in personal order:", personalize(listed, pers_ind))
            GUI.par.names = personalize(listed, pers_ind)
            # print(listed)
            # print(GUI.par.names)
        else:
            com.send_message(sock, com.write_message(0, "Error client: Tag " + str(tag) + "unknown."))
        if rest is None:
            break
        else:
            tag, value, rest, player = com.read_message(rest)

pile_size = 3

pygame.mouse.set_visible(1)
naming = GUI.InputBox(GUI.screen, "Bitte Namen eingeben:")

sock.connect((addr, port))

while True:
    work_sockets([sock])
    GUI.display(draw_pile)
    if not name and naming.wait_input and pers_ind:
        # print("Getting name input")
        name = naming.get_input()
        if name and name != 42:
            # print("Got name input")
            com.send_message(sock, com.write_message(com.tag_usernames, (str(pers_ind) + name)))
    elif name == 42:
        sock.close()
        sys.exit()

    x, y = pygame.mouse.get_pos()

    # blit hand if there are any cards to blit
    if len(GUI.hand) > 0:

        GUI.hand_rectangles, GUI.hand_objects = GUI.show_hand(GUI.hand, x, y, index_big_card)

        # Calculate area of displayed hand depending on actual number of cards
        hand_w = distance * (len(GUI.hand) - 1) + GUI.par.empty_card_w
        hand_area = pygame.Rect((GUI.par.screen_w - hand_w) // 2, card_pos_y, hand_w, GUI.par.empty_card_h)

        # examine which card is selected by the cursors' position
        if hand_area.collidepoint(x, y) and not GUI.drag_card:
            for ind, Rectangle in enumerate(GUI.hand_rectangles):
                if Rectangle.collidepoint(x, y):
                    index_big_card = ind
                    break
                else:
                    index_big_card = -1  # Dürfte keinen Effekt haben

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sock.close()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            if GUI.draw_pile.rect is not None and GUI.draw_pile.touching(x, y):
                GUI.draw_pile.active = True
            if len(GUI.hand) > 0:
                if hand_area.collidepoint(x, y):
                    GUI.drag_card = True
        elif event.type == MOUSEBUTTONUP:
            # if index_big_card <= len(hand):
            #     index_big_card = -1
            if GUI.open_discard_pile.active:
                GUI.open_discard_pile.value = GUI.hand[index_big_card]
                com.send_message(sock, com.write_message(com.tag_open_dis, GUI.open_discard_pile.value, pers_ind))
                GUI.open_discard_pile.active = GUI.discard(index_big_card)
            elif GUI.covered_discard_pile.active:
                com.send_message(sock, com.write_message(com.tag_cov_dis, GUI.hand[index_big_card], pers_ind))
                GUI.covered_discard_pile.active = GUI.discard(index_big_card)
            elif GUI.draw_pile.active:
                com.send_message(sock, com.write_message(com.tag_draw, "draw", pers_ind))
                # print("main loop: draw: pers_ind =", pers_ind)
                GUI.draw_pile.active = False
            GUI.drag_card = False
    if GUI.drag_card and GUI.open_discard_pile.touch:
        GUI.open_discard_pile.active = True
        GUI.covered_discard_pile.active = False
        GUI.show_comment("Karte offen ablegen", (GUI.open_discard_pile.x, GUI.open_discard_pile.x), GUI.par.card_w)
    elif GUI.drag_card and GUI.covered_discard_pile.touch:
        GUI.covered_discard_pile.active = True
        GUI.open_discard_pile.active = False
        GUI.show_comment("Karte verdeckt ablegen", (GUI.open_discard_pile.x, GUI.open_discard_pile.y), GUI.par.card_w)
    elif GUI.draw_pile.active and GUI.draw_pile.touching(x, y) and draw_pile:
        GUI.show_comment("Karte ziehen", (GUI.draw_pile.x, GUI.draw_pile.y), GUI.par.card_w)
    else:
        GUI.open_discard_pile.active = False
        GUI.covered_discard_pile.active = False
        GUI.draw_pile.active = False

    #if not naming.wait_input:
    #    clock.tick(fps)
    pygame.display.update()
