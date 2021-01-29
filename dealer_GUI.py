import pygame.freetype
import sys
from pygame.locals import *
import socket
import com
import create_deck
import GUI


#ToDo: Spielmechanik: dealer kann keine Karten ziehen,
# Stapel aufteilen / auf die Hand nehmen, idealerweise frei auf dem Tisch verschieben (für Stiche nehmen etc.),
# dann auch Möglichkeit, Stapel anzusehen (oder generell bei offenem Stapel)
# Information über Handlungen der Mitspielenden (Chatfenster am Rand o.ä. / PopUp-Meldungen)
# rein GUI: Problem schwarzer Streifen, 'Kreuz' komisch verschoben, Anzahl Karten Spieler auf Stapelrückseite anzeigen
# kann Spielmenü nicht mit Enter bestätigen
# ! Was, wenn zu viele Karten gegeben werden sollen?
# ! IP-Adressen frei eingeben -> Textfeld
# ! Name
# ! Doku / Benutzerhandbuch: Motivation / was kann es, technisch: Netzwerknachrichten beschreiben


deck, players, piles_size = create_deck.results()
GUI.par.other_players = players - 1
GUI.par.set(GUI.par.other_players, 250 // GUI.par.other_players)

players_piles, draw_pile_cards = create_deck.distribute(deck, players, piles_size)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(("127.0.0.1", 1338))
print("Mit Server verbunden")
com.send_message(server,com.write_message(com.tag_prior_user, "secret_message"))
com.send_message(server, com.write_message(com.tag_players, str(players)))

pers_ind = 1
index_big_card = -1

draw = []
msg = None
draw_pile = True
name = None
card_pos_y = GUI.card_pos_y
distance = GUI.distance


def give_cards():
    i = 1
    while i <= players:
        for j in players_piles[i-2]:
            com.send_message(server, com.write_message(com.tag_give_cards, j, i))
        i += 1
    for k in draw_pile_cards:
        com.send_message(server, com.write_message(com.tag_draw_pile, k))


def work_sockets(sockets):
    tag, value, msg, player, sock = com.receiving(sockets)
    while True:
        if tag == com.tag_no_msg:
            break
        elif tag == com.tag_open_dis:
            GUI.open_discard_pile.value = value
        elif tag == com.tag_empty_dp:
            global draw_pile
            draw_pile = int(value)
        elif tag == com.tag_socket_closed:
            GUI.show_comment("Verbindung zum Server verloren.", GUI.par.center, 500)
        elif tag in com.tags_to_all:
            GUI.show_comment(value, GUI.par.center, 200)
            print(value)
        if tag == com.tag_take_cards:
            GUI.hand.append(value)
            print("fcn work_sockets: received  card:", value)
        elif tag == com.tag_usernames:
            GUI.par.names = com.decode_list(value)
        else:
            com.send_message(server, com.write_message(0, "Error client: Tag " + str(tag) + "unknown."))
        if msg is None:
            break
        else:
            tag, value, msg, player = com.read_message(msg)


give_cards()
pygame.init()  # initialize pygame
fps = 30
clock = pygame.time.Clock()
pygame.mouse.set_visible(1)

naming = GUI.InputBox(GUI.screen, "Bitte Namen eingeben:")

while True:
    work_sockets([server])
    GUI.display(draw_pile)
    if name is None and naming.wait_input:
        name = naming.get_input()
        if name and name != 42:
            print(name)
            com.send_message(server, com.write_message(com.tag_usernames, (str(1) + name)))
    elif name == 42:
        server.close()
        pygame.quit()
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
            server.close()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            if GUI.draw_pile.rect is not None and GUI.draw_pile.touching(x, y):
                GUI.draw_pile.active = True
            elif GUI.open_discard_pile.touching(x, y):
                GUI.open_discard_pile.active = True
            elif GUI.covered_discard_pile.touching(x, y):
                GUI.covered_discard_pile.active = True
            if len(GUI.hand) > 0:
                if hand_area.collidepoint(x, y):
                    GUI.drag_card = True
        elif event.type == MOUSEBUTTONUP:
            if GUI.open_discard_pile.active:
                if GUI.drag_card:
                    GUI.open_discard_pile.value = GUI.hand[index_big_card]
                    com.send_message(server, com.write_message(com.tag_open_dis, GUI.open_discard_pile.value, pers_ind))
                    GUI.open_discard_pile.active = GUI.discard(index_big_card)
                else:
                    com.send_message(server,com.write_message(com.tag_shuffle, "open"))
            elif GUI.covered_discard_pile.active:
                if GUI.drag_card:
                    com.send_message(server, com.write_message(com.tag_cov_dis, GUI.hand[index_big_card], pers_ind))
                    GUI.covered_discard_pile.active = GUI.discard(index_big_card)
                else:
                    com.send_message(server, com.write_message(com.tag_shuffle, "cov"))
            elif GUI.draw_pile.active:
                com.send_message(server, com.write_message(com.tag_draw, "draw", 1))
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
    elif GUI.drag_card or not (GUI.open_discard_pile.active or GUI.covered_discard_pile.active):
        GUI.open_discard_pile.active = False
        GUI.covered_discard_pile.active = False
        GUI.draw_pile.active = False

    if not naming.wait_input:
        clock.tick(fps)
    pygame.display.update()
