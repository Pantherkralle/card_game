import pygame
import os
import sys

pygame.init()


class Parameters:
    def __init__(self):
        self.other_players = 1
        self.angle = 0
        self.start_angle = - self.angle * ((self.other_players - 1) // 2)
        self.names = ["Warte auf Spieler*innen."]
        self.piles_places = []
        self.names_places = []
        self.screen_w = 1000
        self.screen_h = 600
        self.center_x = self.screen_w // 2
        self.center_y = self.screen_h // 2
        self.center = (self.center_x, self.center_y)
        self.r = 200
        self.card_w = 36
        self.card_h = 50
        self.empty_card_w = 100
        self.empty_card_h = 150

    def set(self, other_players=None, angle=None):
        if other_players is not None:
            self.other_players = other_players
        if angle is not None:
            self.angle = angle
            self.start_angle = - self.angle * ((self.other_players - 1) // 2)
        self.piles_places = rotation()
        self.names_places = rotation(self.r + 85)

    def name(self, names):
        self.names = names


par = Parameters()


class InputBox:
    def __init__(self, scr, text, w=300, h=150):
        self.scr = scr
        self.center = (scr.get_width()//2, scr.get_height()//2)
        self.w = w
        self.h = h
        self.x, self.y = self.centralize()
        self.text = text
        self.text_object = myfont.render(text, False, (0, 0, 0))
        self.text_input = ""
        self.text_input_object = None
        self.text_h = self.text_object.get_height()
        self.outer_box = pygame.Rect(self.x, self.y, self.w, self.h)
        self.inner_box = pygame.Rect(self.x+5, self.y+self.text_h+5, self.w-10, 30)
        self.wait_input = True

    def show(self):
        self.scr.fill((255, 255, 255), self.outer_box)
        pygame.draw.rect(self.scr, (0, 0, 0), self.inner_box, 1)
        pygame.draw.rect(self.scr, (0, 0, 0), self.outer_box, 2)
        self.scr.blit(self.text_object, (self.x+5, self.y+5))
        if self.text_input_object is not None:
            self.scr.blit(self.text_input_object, (self.x+10, self.y+self.text_h + 5))

    def get_input(self):
        self.show()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 42
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.wait_input = False
                    return self.text_input
                elif event.key == pygame.K_BACKSPACE and len(self.text) > 0:
                    self.text_input = self.text_input[:-1]
                else:
                    self.text_input += event.unicode
            self.text_input_object = myfont.render(self.text_input, False, (0, 0, 0))
            self.scr.blit(self.text_input_object, (self.x+10, self.y+self.text_h+5))
            return None

    def set_center(self, center):
        self.center = center
        self.centralize()

    def centralize(self):
        self.x = self.center[0] - self.w//2
        self.y = self.center[1] - self.h//2
        return self.x, self.y


class Card:
    def __init__(self, im, x=0, y=0, width=None, height=None, angle=None, pos = "big"):
        self.image = im
        if width is not None and height is not None:
            self.image = pygame.transform.scale(im, (width, height))
        if angle is not None:
            self.image = pygame.transform.rotate(self.image, angle)
        self.w = self.image.get_width()
        self.h = self.image.get_height()
        self.x = x
        self.y = y
        self.pos = pos
        self.rectang = None
        self.drag = False
        self.value = None
        self.touch = False
        self.active = False

    def text(self, text):
        self.value = text
        if self.pos in ["left", "right"]:
            text_space = self.h - 20
            text_object, font = fit_text(self.value, text_space)
            text_object = pygame.transform.rotate(text_object, -90)
            if self.pos == "left":
                blit(text_object, (self.x+5, self.y+10)) # Änderung von y-10
            elif self.pos == "right":
                blit(text_object, (self.x+self.w-5-text_object.get_width(), self.y+10)) # Änderung hier von y-10
        elif self.pos == "big":
            line_h, text_objects = line_break(self.image, self.value)
            show_lines(self.image, self.value, (self.x + self.w / 2, self.y + 10)) # vorher x=10, y=-10

    def blit(self, x=None, y=None):
        try:
            blit(self.image, (x, y))
            self.set_position(x, y)
        except:
            blit(self.image, (self.x, self.y))

    def rect(self):
        if self.pos in ["right", "left"]:
            rect_w = distance
        else:
            rect_w = self.w
        if self.pos in ["left", "big"]:
            self.rectang = pygame.Rect(self.x, self.y, rect_w, self.h)
        else:
            self.rectang = pygame.Rect(self.x + self.w - distance, self.y, rect_w, self.h)
        return self.rectang

    def drag(self, cond):
        self.drag = cond

    def touching(self, x, y):
        self.rect()
        self.touch = self.rectang.collidepoint(x, y)
        return self.touch

    def scale(self, w, h):
        self.w = w
        self.h = h
        self.image = pygame.transform.scale(self.image, (w, h))

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def centre(self):
        """
        Creates a vector to move Card's defined location from its upper left corner to its center.

        Returns
        -------
        Vector2D
        """
        v = pygame.math.Vector2()
        v.x = - self.w // 2
        v.y = - self.h // 2
        return v


def load_image(title, width=None, height=None):
    """
    Loads an image from the project's folder and scales it.

    Parameters
    ----------
    title: str
        Title of the image's file to be loaded.
    width: int, optional
        Width of the scaled image
    height: int, optional
        Height of the scaled image.

    Returns
    -------
    image object
    """
    try:
        image = pygame.image.load(os.path.join("Kartenspiel", title))
    except:
        image = pygame.image.load(os.path.join(title))
    if width is not None and height is not None:
        image = pygame.transform.scale(image, (width, height))
    return image


def centre(obj):
    """
    Creates a vector to move an object's defined location from its upper left corner to its center.

    Parameters
    ---------
    obj: pygame.Surface
        The object to be relocated.

    Returns
    -------
    Vector2D
    """
    object_w = obj.get_width()
    object_h = obj.get_height()
    v = pygame.math.Vector2()
    v.x = - object_w // 2
    v.y = - object_h // 2
    return v


def rotation(length=par.r):
    """
    Creates as many spots as other players participate in game around the table.

    Parameters
     ---------
    length: int
        Distance of each spot to center of the table.

    Returns
    -------
    list
        Coordinates of each spot created.
    """
    op = par.other_players

    v = pygame.math.Vector2()
    v.x = 0
    v.y = -length
    v.rotate_ip(par.angle * (op - 1) / 2)
    places = [par.center + v]
    i = 1
    while i < op:
        v.rotate_ip(-par.angle)
        places.append(par.center + v)
        i = i + 1
    return places


def piles_pos(x_dist):
    pos = par.center + centre(card_back) + (x_dist * 2 * par.card_w, 0)
    return pos


screen = pygame.display.set_mode((par.screen_w, par.screen_h))

background = load_image("white.png", par.screen_w, par.screen_h)
table = load_image("background.png", 2 * par.r + 100, 2 * par.r + 100)
card_back = load_image("card_back.png", par.card_w, par.card_h)
cb_inact = load_image("card_back_inactive.png", par.card_w, par.card_h)
empty_card = load_image("empty_card.png", par.empty_card_w, par.empty_card_h)

myfont = pygame.font.SysFont('Arial', 20)                                                           # eigene Schrift!
littlefont = pygame.font.SysFont('Arial', 10)

draw_pile = Card(card_back, piles_pos(0)[0], piles_pos(0)[1])
open_discard_pile = Card(empty_card, piles_pos(-1)[0], piles_pos(-1)[1], par.card_w, par.card_h)
covered_discard_pile = Card(card_back, piles_pos(1)[0], piles_pos(1)[1])

par.piles_places = rotation()
names_places = rotation(par.r + 85)
card_pos_y = par.screen_h - 150
distance = 25

drag_card = False

pygame.display.set_caption('Kartenspiel')

hand = []
hand_objects = []
hand_rectangles = []


def names_default(op=par.other_players):
    nl = ['server']
    a = 1
    while a <= op:
        nl.append("player {}".format(a))
        a = a + 1
    return nl


def fit_text(text, w, font_size=20):
    font = pygame.font.SysFont('Arial', font_size)
    text_object = (font.render(text, False, (0, 0, 0)))
    while text_object.get_width() > w:
        font_size -= 1
        font = pygame.font.SysFont('Arial', font_size)
        text_object = (font.render(text, False, (0, 0, 0)))
    return text_object, font


def line_break(surface, text):
    """
    Splits card names up in several lines if too long for one and reduces size of font depending on longest word.

    Parameters:
    -----------
    surface: pygame.Surface object
        Surface on that the text is to be shown.
    text: str
        Text to be rendered.

    Returns
    -------
    int
        Height of each line.
    list of str
        List of lines to be rendered one by one.
    """
    surface_w = surface.get_width()
    lines = []
    line = ""
    text_objects = []
    if text == "":
        return 0, 0
    if " " in text:
        words = text.split()
    else:
        words = [text]
    for i in words:
        text_object, font = fit_text(i, surface_w)
        line_h = text_object.get_height()
    for word in words:
        line_object = font.render(line + word, False, (0, 0, 0))
        if line_object.get_width() <= surface_w:
            line = line + " " + word
        else:
            lines.append(line)
            text_objects.append(font.render(line, False, (0, 0, 0)))
            line = word
    lines.append(line)
    text_objects.append(font.render(line, False, (0, 0, 0)))
    return line_h, text_objects


def show_lines(surface, text, position):
    line_h, lines = line_break(surface, text)
    if lines == 0:
        return
    for index, line in enumerate(lines):
        x = int(position[0] - line.get_width() / 2)
        y = int(position[1] + index * line_h)
        blit(line, (x, y))


class Comment:

    def __init__(self, text, surface=background, pos=None, w=par.screen_w//2):
        self.center = par.center
        self.text = text
        self.text_object = myfont.render(self.text, False, (0,0,0))
        self.bg = pygame.transform.scale(surface, (w, par.screen_h))
        line_h, line_objects = line_break(self.bg, self.text)
        self.w = w
        self.h = line_h * len(line_objects) * 2
        if pos is None:
            self.x = self.centralize()[0]
            self.y = self.centralize()[1]
        else:
            self.x = pos[0]
            self.y = pos[1]
        self.rectang = pygame.Rect(self.x, self.y, self.w, self.h)

    def show(self):
        self.bg = pygame.transform.scale(self.bg, (self.w, self.h))
        blit(self.bg, (self.x, self.y))
        pygame.draw.rect(screen, (0,0,0), self.rectang, 2)
        show_lines(self.bg, self.text, (self.center[0], self.y+self.h//4))

    def centralize(self):
        self.x = self.center[0] - self.w//2
        self.y = self.center[1] - self.h//2
        return self.x, self.y


def show_comment(comment, pos, w):
    comment_text = myfont.render(comment, False, (0, 0, 0))
    comment_text_w = comment_text.get_width()
    comment_text_h = comment_text.get_height()
    comment_bg = pygame.transform.scale(empty_card, (comment_text_w + 6, comment_text_h))
    blit(comment_bg, pos + (centre(comment_text)[0] + w / 2 - 3, - 10 - comment_text_h))
    blit(comment_text, pos + (centre(comment_text)[0] + w / 2, - 10 - comment_text_h))


def rotoblit(surface, places, start_angle=par.start_angle, roto_angle=par.angle):
    angle = start_angle
    for j in places:
        card = Card(surface, par.card_w, par.card_h, angle=angle)
        blit(card.image, j + centre(card.image))
        angle = angle + roto_angle
    return angle


def roundtext(places=par.names_places, texts=par.names):
    for index, n in enumerate(texts):
        text = myfont.render(n, False, (0, 0, 0))
        v_text = centre(text)
        blit(text, places[index] + v_text)


def sidecards(index, text, pos_x, right=False):
    card = hand_objects[index]
    card.scale(par.empty_card_w, par.empty_card_h)
    card.blit(pos_x, card_pos_y - 10)
    if right:
        card.pos = "right"
        index = -(index + 1)
        pos_x = pos_x - distance
    else:
        card.pos = "left"
        pos_x = pos_x + distance
    card.text(text)
    card.rect()
    hand_rectangles[index] = card.rectang
    hand_objects[index] = card
    return pos_x


def show_hand(deck, x, y, ibc):
    if len(deck) <= 0:
        return 0, 0

    hand_w = distance * (len(deck) - 1) + par.empty_card_w
    hand_pos_x = par.screen_w // 2 - hand_w // 2

    global hand_rectangles
    while len(hand_rectangles) < len(deck):
        hand_rectangles.append(None)
    while len(hand_objects) < len(deck):
        hand_objects.append(Card(empty_card, width=par.empty_card_w, height=par.empty_card_h))


    if ibc == -1:
        index_big = len(deck) - 1
    else:
        index_big = ibc

    for index, m in enumerate(deck):
        if index < index_big:
            hand_pos_x = sidecards(index, m, hand_pos_x)
        elif index == index_big:
            hand_pos_x = par.screen_w // 2 + hand_w // 2 - par.empty_card_w
            break

    for index, m in enumerate(reversed(deck[index_big:])):
        index_big_reversed = len(deck[index_big + 1:])
        if index < index_big_reversed:
            hand_pos_x = sidecards(index, m, hand_pos_x, True)
        else:
            big_card = hand_objects[index_big]
            big_card.pos = "big"
            big_card.scale(par.empty_card_w, par.empty_card_h)
            if drag_card:
                if open_discard_pile.touching(x, y):
                    big_card.scale(par.card_w, par.card_h)                                     #ToDo: sorgt für Schwarze
                    big_card.blit(open_discard_pile.x + 10, open_discard_pile.y + 10)
                    big_card.text(m)
                elif covered_discard_pile.touching(x, y):
                    blit(card_back, (covered_discard_pile.x + 10, covered_discard_pile.y + 10))
                else:
                    big_card.scale(par.empty_card_w, par.empty_card_h)
                    big_card.blit(x + big_card.centre()[0], y + big_card.centre()[1])
                    big_card.text(m)
                    hand_rectangles[index_big] = big_card.rect()
            else:
                big_card.blit(hand_pos_x, card_pos_y - 10)
                big_card.text(m)
                hand_rectangles[index_big] = big_card.rect()
    return hand_rectangles, hand_objects


def discard(ibc):
    hand_rectangles.pop(ibc)
    hand.pop(ibc)
    return False


def display(draw_cond):
    blit(background, (0, 0))
    blit(table, par.center + centre(table))

    # blit draw pile and discard piles
    if draw_cond:
        draw_pile.blit()
    else:
        draw_pile.rectang = None

    open_discard_pile.blit()
    if open_discard_pile.value is not None:
        open_discard_pile.text(open_discard_pile.value)

    covered_discard_pile.blit()

    # blit players' card piles and names
    rotoblit(card_back, par.piles_places)
    roundtext(par.names_places, par.names[1:])


def blit(obj, position):
    screen.blit(obj, position)
