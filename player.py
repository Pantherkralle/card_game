import tkinter as tk


# ToDo: Spielmechanik: dealer kann keine Karten ziehen,
# Stapel aufteilen / auf die Hand nehmen, idealerweise frei auf dem Tisch verschieben (für Stiche nehmen etc.),
# dann auch Möglichkeit, Stapel anzusehen (oder generell bei offenem Stapel)
# Information über Handlungen der Mitspielenden (Chatfenster am Rand o.ä. / PopUp-Meldungen)
# rein GUI: Problem schwarzer Streifen, 'Kreuz' komisch verschoben, Anzahl Karten Spieler auf Stapelrückseite anzeigen
# kann Spielmenü nicht mit Enter bestätigen
# ! Was, wenn zu viele Karten gegeben werden sollen?
# ! IP-Adressen frei eingeben -> Textfeld
# ! Name
# ! Doku / Benutzerhandbuch: Motivation / was kann es, technisch: Netzwerknachrichten beschreiben


class StartMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.sw_name = self.create_subwindow()
        self.sw_ip = self.create_subwindow()
        self.sw_port = self.create_subwindow()

        self.name = self.create_text_widget(self.sw_name)
        self.role_var = tk.IntVar(self.root, value=1)
        self.ip = self.create_text_widget(self.sw_ip)
        self.port = self.create_text_widget(self.sw_port)

        self.warn = False
        self.name_res, self.role_res, self.ip_res, self.port_res = None, None, None, None

        self.__call__()

    def __call__(self):
        name_label = tk.Label(self.sw_name, text="Name:")
        name_label.grid(column=0, row=0)
        self.name.grid(column=1, row=0)
        self.sw_name.grid(row=0, sticky="E")

        join = tk.Radiobutton(self.root, text='Spiel beitreten', variable=self.role_var, value=0)
        create = tk.Radiobutton(self.root, text='Spiel erstellen', variable=self.role_var, value=1)
        join.grid(row=1, sticky="W")
        create.grid(row=2, sticky="W")

        conn_label = tk.Label(text="Verbindung zum Server:")
        conn_label.grid(row=3, sticky="W")

        ip_label = tk.Label(self.sw_ip, text="IP-Adresse:")
        ip_label.grid(column=0, row=0)
        self.ip.grid(column=1, row=0)
        self.sw_ip.grid(row=4)

        port_label = tk.Label(self.sw_port, text="Port:")
        port_label.grid(column=0, row=0)
        self.port.grid(column=1, row=0)
        self.sw_port.grid(row=5, sticky="E")

        submit = tk.Button(text="Loslegen!", command=self.results)
        submit.grid(row=6)

        if self.warn:
            self.warning()

        self.root.protocol("WM_DELETE_WINDOW", quit)

        tk.mainloop()

    def results(self):
        self.role_res = self.role_var.get()
        self.name_res = self.get_text(self.name)
        self.ip_res = self.get_text(self.ip)
        self.port_res = int(self.get_text(self.port))
        print(self.name_res, self.ip_res, self.port_res)
        if not (self.name_res and self.ip_res and self.port_res):
            self.warn = True
            self.__call__()
        else:
            self.root.destroy()

    def warning(self):
        warn = tk.Label(self.root, text="Du musst einen Namen, eine IP-Adresse \nund einen Port eingeben - \nsonst geht's hier nicht weiter :)")
        warn.grid(row=7)

    def create_subwindow(self):
        return tk.PanedWindow(self.root, orient="vertical")

    def get_text(self, text_widget):
        return text_widget.get("1.0", 'end-1c')

    def create_text_widget(self, parent):
        return tk.Text(parent, height=1, width=20)


def connect(ip, port, name, role):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((ip, port))
    com.send_message(server, com.write_message(com.tag_socket_connected, name, role))
    return server


menu = StartMenu()
if menu.role_res:
    import create_deck
import GUI
import pygame
from pygame.locals import *
import socket
import sys
import com

pers_ind = None
draw_pile = True

index_big_card = -1
card_pos_y = GUI.card_pos_y
distance = GUI.distance


def process_sockets(sockets):
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
        elif tag == com.tag_start:
                GUI.par.name(personalize(com.decode_list(value), pers_ind))
                print(GUI.par.names)
                GUI.par.other_players = len(GUI.par.names) - 1
                GUI.par.set(GUI.par.other_players, 250 // GUI.par.other_players)
        elif tag in [com.tag_yet_to_start, com.tag_socket_closed]:
            note = GUI.Comment(
                "Verbindung zum Server konnte nicht hergestellt werden, da Spiel noch nicht gestartet "
                "oder bereits alle Spielenden anwesend.")
            note.show()
            pygame.display.update()
            clock.tick(1 / 5)
            pygame.quit()
            quit()
        elif tag == com.tag_take_cards:
            GUI.hand.append(value)
        else:
            com.send_message(sock, com.write_message(0, "Error client: Tag " + str(tag) + "unknown."))
        if rest is None:
            break
        else:
            tag, value, rest, player = com.read_message(rest)


if menu.role_res:
    deck, players, piles_size = create_deck.results()
    players_piles, draw_pile_cards = create_deck.distribute(deck, players, piles_size)

    server = connect(menu.ip_res, menu.port_res, menu.name_res, players)

    def personalize(listed, per_ind):
        return listed

    def give_cards():
        i = 1
        while i <= players:
            for j in players_piles[i - 2]:
                com.send_message(server, com.write_message(com.tag_give_cards, j, i))
            i += 1
        for k in draw_pile_cards:
            com.send_message(server, com.write_message(com.tag_draw_pile, k))

    give_cards()

else:
    server = connect(menu.ip_res, menu.port_res, menu.name_res, menu.role_res)

    def personalize(listed, per_ind):
        print(listed)
        print(per_ind)
        pers_list = listed[per_ind - 1:]
        for element in listed[:per_ind - 1]:
            pers_list.append(element)
        return pers_list


pygame.init()  # initialize pygame
fps = 30
clock = pygame.time.Clock()
pygame.mouse.set_visible(1)

while True:
    process_sockets([server])

    GUI.display(draw_pile)

    x, y = pygame.mouse.get_pos()

    # blit hand if there are any cards to blit
    if len(GUI.hand) > 0:

        GUI.hand_rectangles, GUI.hand_objects = GUI.show_hand(GUI.hand, x, y, index_big_card)
        print(GUI.par.names, pers_ind)
        GUI.show_comment(GUI.par.names[0], (100, GUI.par.screen_h - 50), GUI.par.card_w)

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
                    com.send_message(server,
                                     com.write_message(com.tag_open_dis, GUI.open_discard_pile.value, pers_ind))
                    GUI.open_discard_pile.active = GUI.discard(index_big_card)
                else:
                    com.send_message(server, com.write_message(com.tag_shuffle, "open"))
            elif GUI.covered_discard_pile.active:
                if GUI.drag_card:
                    com.send_message(server, com.write_message(com.tag_cov_dis, GUI.hand[index_big_card], pers_ind))
                    GUI.covered_discard_pile.active = GUI.discard(index_big_card)
                else:
                    com.send_message(server, com.write_message(com.tag_shuffle, "cov"))
            elif GUI.draw_pile.active:
                com.send_message(server, com.write_message(com.tag_draw, "draw", pers_ind))
                GUI.draw_pile.active = False
            GUI.drag_card = False
    if GUI.drag_card and GUI.open_discard_pile.touch:
        GUI.open_discard_pile.active = True
        GUI.covered_discard_pile.active = False
        GUI.show_comment("Karte offen ablegen", (GUI.open_discard_pile.x, GUI.open_discard_pile.x), GUI.par.card_w)
    elif GUI.drag_card and GUI.covered_discard_pile.touch:
        GUI.covered_discard_pile.active = True
        GUI.open_discard_pile.active = False
        GUI.show_comment("Karte verdeckt ablegen", (GUI.open_discard_pile.x, GUI.open_discard_pile.y),
                         GUI.par.card_w)
    elif GUI.draw_pile.active and GUI.draw_pile.touching(x, y) and draw_pile:
        GUI.show_comment("Karte ziehen", (GUI.draw_pile.x, GUI.draw_pile.y), GUI.par.card_w)
    elif GUI.drag_card or not (GUI.open_discard_pile.active or GUI.covered_discard_pile.active):
        GUI.open_discard_pile.active = False
        GUI.covered_discard_pile.active = False
        GUI.draw_pile.active = False

    clock.tick(fps)
    pygame.display.update()
