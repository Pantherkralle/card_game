# import pygame.freetype
# import sys
import pygame
from pygame.locals import *
import socket
import com
import create_deck
import GUI
import tkinter as tk


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
        self.port_res = self.get_text(self.port)
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


def connect(sock, ip, port):
    sock.connect((ip, port))
    tag, value, msg, player, sock = com.receiving([sock], 3)
    if not tag == com.tag_accepted:  # ToDo: Server schickt das noch nicht
        if value is not None:
            print(value)
        else:
            print("Verbindung zum Server konnte nicht hergestellt werden.")
        quit()


def deal(sock):
    import create_deck
    deck, players, piles_size = create_deck.results()
    players_piles, draw_pile_cards = create_deck.distribute()
    com.send_message(sock, com.write_message(com.tag_players, str(players)))
    com.give_cards([sock] * players, players_piles)


class Graphics:

    def __init__(self, name):
        pygame.init()
        pygame.mouse.set_visible(1)
        self.clock = pygame.time.Clock()
        self.fps = 30
        self.x, self.y = pygame.mouse.get_pos()
        self.index_big_card = -1
        self.distance = GUI.distance
        self.card_pos_y = GUI.card_pos_y
        self.draw_pile = True
        self.name = name

    def update(self, sock):
        self.show_hand()
        self.handle_events(sock)
        self.clock.tick(self.fps)
        pygame.display.update()

    def handle_events(self, sock):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sock.close()
                quit()
            elif event.type == MOUSEBUTTONDOWN:
                if GUI.draw_pile.rect is not None and GUI.draw_pile.touching(self.x, self.y):
                    GUI.draw_pile.active = True
                elif GUI.open_discard_pile.touching(self.x, self.y):
                    GUI.open_discard_pile.active = True
                elif GUI.covered_discard_pile.touching(self.x, self.y):
                    GUI.covered_discard_pile.active = True
                if len(GUI.hand) > 0:
                    if self.hand_area.collidepoint(self.x, self.y):
                        GUI.drag_card = True
            elif event.type == MOUSEBUTTONUP:
                if GUI.open_discard_pile.active:
                    if GUI.drag_card:
                        GUI.open_discard_pile.value = GUI.hand[self.index_big_card]
                        com.send_message(sock, com.write_message(com.tag_open_dis, GUI.open_discard_pile.value, pers_ind))
                        GUI.open_discard_pile.active = GUI.discard(self.index_big_card)
                    else:
                        com.send_message(sock, com.write_message(com.tag_shuffle, "open"))
                elif GUI.covered_discard_pile.active:
                    if GUI.drag_card:
                        com.send_message(sock, com.write_message(com.tag_cov_dis, GUI.hand[self.index_big_card], pers_ind))
                        GUI.covered_discard_pile.active = GUI.discard(self.index_big_card)
                    else:
                        com.send_message(sock, com.write_message(com.tag_shuffle, "cov"))
                elif GUI.draw_pile.active:
                    com.send_message(sock, com.write_message(com.tag_draw, "draw", 1))
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
        elif GUI.draw_pile.active and GUI.draw_pile.touching(self.x, self.y) and self.draw_pile:
            GUI.show_comment("Karte ziehen", (GUI.draw_pile.x, GUI.draw_pile.y), GUI.par.card_w)
        elif GUI.drag_card or not (GUI.open_discard_pile.active or GUI.covered_discard_pile.active):
            GUI.open_discard_pile.active = False
            GUI.covered_discard_pile.active = False
            GUI.draw_pile.active = False

    def show_hand(self):
        GUI.hand_rectangles, GUI.hand_objects = GUI.show_hand(GUI.hand, self.x, self.y, self.index_big_card)

        # Calculate area of displayed hand depending on actual number of cards
        hand_w = self.distance * (len(GUI.hand) - 1) + GUI.par.empty_card_w
        self.hand_area = pygame.Rect((GUI.par.screen_w - hand_w) // 2, self.card_pos_y, hand_w, GUI.par.empty_card_h)

        # examine which card is selected by the cursors' position
        if self.hand_area.collidepoint(self.x, self.y) and not GUI.drag_card:
            for ind, Rectangle in enumerate(GUI.hand_rectangles):
                if Rectangle.collidepoint(self.x, self.y):
                    self.index_big_card = ind
                    break
                else:
                    self.index_big_card = -1  # ToDo: Dürfte keinen Effekt haben


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
            com.send_message(sockets[0], com.write_message(0, "Error client: Tag " + str(tag) + "unknown."))
        if msg is None:
            break
        else:
            tag, value, msg, player = com.read_message(msg)


def run():
    menu = StartMenu()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect(sock, menu.ip_res, menu.port_res)

    com.send_message(sock, com.write_message(com.tag_usernames, str(menu.role_res) + menu.name_res))
    if menu.role_res:
        deal(sock)

    gui = Graphics(menu.name_res)