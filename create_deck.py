from tkinter import *
import random

# create class for PanedWindows with a removal function


class Subwindow:
    def __init__(self, col=None, row=None, parent=None):
        self.pw = PanedWindow(parent, orient=VERTICAL)
        self.col = col
        self.row = row

    def show(self):
        # self.pw.pack(fill=BOTH, expand=True)
        self.pw.grid(column=self.col, row=self.row, sticky="W")

    def remove(self):
        self.pw.grid_forget()


class LabelAnd:
    def __init__(self, parent, text, row):
        self.textw = Label(parent.pw, text=text)
        self.textw.grid(column=0, row=row)
        self.var = None


class LabelAndSpinbox(LabelAnd):
    def __init__(self, parent, text, row, fr=1, to=10, start=1):
        super().__init__(parent, text, row)
        try:
            self.var = IntVar(parent.pw, value=start)
            self.spin = Spinbox(parent.pw, from_=fr, to=to, textvariable=self.var, width=3)
        except:
            self.var = IntVar(parent, value=start)
            self.spin = Spinbox(parent, from_=fr, to=to, textvariable=self.var, width=3)
        self.spin.grid(column=1, row=row)


class LabelAndInput:
    def __init__(self, parent, text, row, num=0):
        self.parent = parent
        self.text = text
        self.row = row
        self.left_list = []
        self.right_list = []
        self.multilines(num)

    def multilines(self, num):
        i = len(self.left_list)
        while i > num:
            self.left_list[-1].grid_forget()
            self.right_list[-1].grid_forget()
            self.left_list.pop(-1)
            self.right_list.pop(-1)
            i -= 1
        while i < num:
            left = self.left_element(i)
            left.grid(column=0, row=self.row+i, sticky="E")
            right = self.right_element()
            right.grid(column=1, row=self.row+i, sticky="E")
            self.left_list.append(left)
            self.right_list.append(right)
            i += 1

    def left_element(self, position):
        name = self.text + ' ' + str(position + 1)
        return Label(self.parent.pw, text=name)

    def right_element(self):
        return Text(self.parent.pw, height=1, width=20)


class InputAndSpinbox(LabelAndInput):
    def __init__(self, parent, num=0, first_row=0, fr=1, to=10):
        self.fr, self.to = fr, to
        super().__init__(parent, None, first_row, num)

    def left_element(self, position):
        try:
            return Text(self.parent.pw, height=1, width=20)
        except:
            return Text(self.parent, height=1, width=20)

    def right_element(self):
        try:
            return Spinbox(self.parent.pw, from_=self.fr, to=self.to, width=3)
        except:
            return Spinbox(self.parent, from_=self.fr, to=self.to, width=3)

    def toggle_spin(self, var):
        if var.get():
            for i, sb in enumerate(self.right_list):
                sb.grid(column=1, row=self.row+i)

        else:
            for sb in self.right_list:
                sb.grid_forget()


def show_and_forget(pw, cond):
    if cond.get():
        pw.show()
        print(True)
    else:
        pw.pw.grid_forget()
        print(False)

def update_text(var):
    if var.get():
        return 'Anzahl unterschiedlicher Karten je Spielfarben'
    else:
        return 'Anzahl unterschiedlicher Karten'

# create tkinter window
root = Tk()

# create PanedWindow to contain the selection of decks ---------------------------------------------------------------
choose_deck = Subwindow(row=0)

players = Subwindow(parent=choose_deck.pw)
players_num = LabelAndSpinbox(players, 'Anzahl der Spielenden', 0, 1, 30)
players_num.var.set(3)
piles_size = LabelAndSpinbox(players, 'Anzahl der Karten pro Spieler*in', 1, 1, 30)
piles_size.var.set(10)

# the selection of decks consists of buttons
choose_var = IntVar(root, value=1)
but_choose_french = Radiobutton(choose_deck.pw, text='Französisches Blatt', variable=choose_var, value=1,
                                command=lambda: [create_own.remove(), create_french.show()])
but_choose_own = Radiobutton(choose_deck.pw, text='Eigenes Deck', variable=choose_var, value=2,
                             command=lambda: [create_french.remove(), create_own.show()])

# add the elements to the PanedWindow
choose_deck.pw.add(players.pw)
choose_deck.pw.add(but_choose_french)
choose_deck.pw.add(but_choose_own)

# show PanedWindow
choose_deck.show()


# create PanedWindow to contain options for French card game creation --------------------------------------------------
create_french = Subwindow(row=1)

title_french = Label(create_french.pw, text='Erstelle französisches Blatt')
title_french.grid(row=0, sticky="W")

lowest_card = LabelAnd(create_french, 'Niedrigste Karte im Deck', 1)
lowest_card_var = IntVar(create_french.pw, value=2)
lowest_card_slide = Scale(create_french.pw, orient=HORIZONTAL, from_=2, to=10, variable=lowest_card_var)
lowest_card_slide.grid(column=1, row=1, sticky="W")

number_sets = LabelAndSpinbox(create_french, 'Anzahl der Sätze im Deck', 2)

number_jokers = LabelAndSpinbox(create_french, 'Anzahl der Joker im Deck', 3, 0)

create_french.show()

# create Pained Window tp contain options for creation of an individual deck -------------------------------------------
create_own = Subwindow(row=1)

title_own = Label(create_own.pw, text='Erstelle individuelles Deck')
title_own.grid(row=0, sticky="W")

colors = Subwindow(row=1, parent=create_own.pw)
define_colors = Subwindow(row=1, parent=colors.pw)

several_colors_var = BooleanVar(create_own.pw, value=False)
several_colors_cb = Checkbutton(colors.pw, text='Mehrere Spielfarben vorhanden',
                                command=lambda: [show_and_forget(define_colors, several_colors_var),
                                                 name_colors.multilines(number_colors.var.get())],
                                variable=several_colors_var)
several_colors_cb.grid(row=0)

number_colors = LabelAndSpinbox(define_colors, 'Anzahl der unterschiedlichen Spielfarben', 0, 2)
name_colors = LabelAndInput(define_colors, 'Spielfarbe', 2)

diff_nums_var = BooleanVar(create_own.pw, value=True)
diff_nums = Checkbutton(create_own.pw, text='Karten unterschiedlich oft vorhanden', variable=diff_nums_var)
diff_nums.grid(row=2)

numbers = Subwindow(row=3, parent=create_own.pw)
num_vals = LabelAndSpinbox(numbers, 'Anzahl unterschiedlicher Spielkarten', 0)


# ToDo: update text depending on several_colors_var
number_colors.spin.configure(command=lambda: [name_colors.multilines(number_colors.var.get())])
values = Subwindow(row=1, parent=numbers.pw)
values_lines = InputAndSpinbox(values, num_vals.var.get())
diff_nums.config(command=lambda: values_lines.toggle_spin(diff_nums_var))
num_vals.spin.config(command=lambda: [values_lines.multilines(num_vals.var.get()),
                                      values_lines.toggle_spin(diff_nums_var)])

values.show()
numbers.show()
colors.show()

num_sets = LabelAndSpinbox(create_own, 'Anzahl der Sätze im Deck', 4)

specials = Subwindow(row=5, parent=create_own.pw)
num_specs = LabelAndSpinbox(specials, 'Anzahl unterschiedlicher Zusatzkarten', 0, 0)
vals_specs = InputAndSpinbox(specials, 1, 1)
num_specs.spin.configure(command=lambda:vals_specs.multilines(num_specs.var.get()))

specials.show()

submit = Subwindow(row=2)
submit_but = Button(submit.pw, text='Deck erstellen')
submit.pw.add(submit_but)
submit.show()


def read_multiple_text_vars(list):
    vars = []
    for element in list:
        vars.append(element.get("1.0", 'end-1c'))
    return vars


def multiply_text(textlist, numlist):
    res = []
    for text, number in zip(textlist, numlist):
        res.extend([text.get("1.0", 'end-1c')] * int(number.get()))
    return res


def combine_cards(colours, numbers):
    """
    Combines colours and numbers to a card deck.

    Parameters
    ----------
    colours: list[str]
        list of colours included in the deck
    numbers: list[str]
        list of numbers included in the deck

    Returns
    -------
    list[str]
        Card deck.
    """
    deck = []
    for c in colours:
        for n in numbers:
            deck = deck + [c + " " + n]
    return deck


def franz_blatt(start, sets, joker):
    """
    Creates a deck based on the French card game sheet.

    Returns
    -------
    list
        list of names of each card in the deck.
    """
    colours = ["Kreuz ", "Pik ", "Herz ", "Karo "]                      # Einfachere Möglichkeit für Aufzählung?
    numbers = ["02", "03", "04", "05", "06", "07", "08", "09", "10", "Bube", "Dame", "König", "Ass"]
    # start = int(input("Niedrigste Karte im Deck (Zahl zwischen 2 und 10) "))
    numbers = numbers[start-2:]
    deck = combine_cards(colours, numbers)
    # sets = int(input("Wie viele Sätze der eingegebenen Karten hat dieses Deck? "))
    deck = deck * sets
    # joker = int(input("Wie viele Joker sind vorhanden? (Zahl >= 0) "))
    deck = deck + ["Joker"] * joker
    return (deck)


class Results():
    def __init(self):
        self.values = None
        self.players = None
        self.piles_size = None

    def get(self):
        # 1: save french card game
        if choose_var.get() == 1:
            self.values = franz_blatt(lowest_card_var.get(), number_sets.var.get(), number_jokers.var.get())
        elif choose_var.get() == 2:
            index = int(num_vals.var.get())
            if diff_nums_var.get():
                self.values = multiply_text(values_lines.left_list[: index], values_lines.right_list[: index])
            else:
                self.values = read_multiple_text_vars(values_lines.left_list[: index])
            if several_colors_var.get():
                colors = read_multiple_text_vars(name_colors.right_list[: int(number_colors.var.get())])
                self.values = combine_cards(colors, self.values)
            self.values *= num_sets.var.get()
            index = int(num_specs.var.get())
            self.values.extend(multiply_text(vals_specs.left_list[: index], vals_specs.right_list[: index]))
        root.destroy()
        print(self.values)
        self.players = players_num.var.get()
        self.piles_size = piles_size.var.get()

    def __call__(self):
        return self.values, self.players, self.piles_size


results = Results()
submit_but.config(command=results.get)
root.protocol("WM_DELETE_WINDOW", results.get)

mainloop()


def distribute(draw_pile, players, piles_size):                                           # Karten mischen und verteilen
    """
    Shuffles card deck and creates a list of the hand of each player and one of the remaining cards.

    Parameters
    ----------
    draw_pile: list
        list of names of cards  to be given.
    players: int
        number of players in the game.

    Returns
    -------
    list
        list of hand of each player.
    list
        list of remaining cards.
    int
        size of each player's hand.
    """
    random.shuffle(draw_pile)
    i = 0
    piles = [None] * players
    while i <= players - 1:
        piles[i] = draw_pile[i * piles_size: (i + 1) * piles_size]
        i = i + 1
    draw_pile = draw_pile[players * piles_size:]
    return piles, draw_pile