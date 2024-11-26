from bakery import assert_equal
from drafter import *
from dataclasses import dataclass
import requests
from word_list import easy, medium, hard
import random


hide_debug_information()
set_website_title("Hangman!!!")
set_website_framed(False)


add_website_css("""
body {
    background-color: lightblue;
}
""")
image_list = ['rightleg.png', 'leftleg.png', 'back.png', 'rightarm.png', 'leftarm.png', 'neck.png', 'head.png', 'empty.png']

@dataclass
class State:
    lives: int
    guesses: list[str]
    word: str
    progress: list[str]
    wins: int
    streak: bool
    total_plays: int
    mode: str


def make_str(this_list: list[str]) -> str:
    this_str = ""
    for item in this_list:
        this_str+=item+" "
    return this_str

def get_word(mode: str) -> str:
    if mode == "Easy":
        easy_num = random.randint(0,13981)
        word = easy[easy_num].upper()
    elif mode == "Intermediate":
        med_num = random.randint(0,69352)
        word = medium[med_num].upper()
    elif mode == "Hard":
        hard_num = random.randint(0, 94851)
        word = hard[hard_num].upper()
    else:
        return 'error'
    return word

@route
def home(state: State) -> Page:
    """
    Displays hangman image, guesses, and progress
    """
    guesses_str = make_str(state.guesses)
    progress_str = make_str(state.progress)
    image_path = image_list[state.lives]
    
    return Page(state, [
        "Let's play Hangman!!",
        bold(progress_str),
        change_margin(float_right(change_height(Image(image_path), '300px')), '0px 200px'),
        change_width(change_height(change_border(Div(Header("Guesses:", 6), guesses_str), 'solid'), '300px'), '40%'), #, {'style_border': 'solid'}
        TextBox('guess'),
        Button("Submit", make_guess),
    ])


@route
def play_game(state: State, mode:str) -> Page:
    state.mode=mode
    state.lives = 7
    state.guesses = []
    state.word = get_word(state.mode)
    state.progress = []
    for letter in state.word:
        state.progress.append('_')
    return home(state)


@route
def index(state: State) -> Page:
    """
    Splash screen
    """
    return Page(state, [
        Image('temp_splash_screen.jpg'),
        SelectBox('mode', ['Easy', 'Intermediate', 'Hard']),
        Button("Play Game!", play_game)
        ])


@route
def make_guess(state: State, guess: str) -> Page:
    if len(guess)!=1 or not guess.isalpha():
        return home(state)
    if guess.upper() in state.guesses:
        return home(state)
    state.guesses.append(guess.upper())
    for letter in state.word:
        if guess.upper() == letter:
            return correct_guess(state, guess)
    return wrong_guess(state)

@route
def wrong_guess(state: State) -> Page:
    state.lives -= 1
    if state.lives > 0:
        return home(state)
    return loss(state)

@route
def correct_guess(state: State, guess) -> Page:
    for i, letter in enumerate(state.word):
        if guess.upper() == letter:
            state.progress[i]=letter
    progress_str = make_str(state.progress)
    if "_" in progress_str:
        return home(state)
    return win(state)


@route
def loss(state: State) -> Page:
    guesses_str = make_str(state.guesses)
    progress_str = make_str(state.progress)

    state.streak = False
    state.total_plays+=1
    return Page(state, [
        "The word was "+str(state.word),
        progress_str,
        change_margin(float_right(change_height(Image('rightleg.png'), '300px')), '0px 200px'),
        change_width(change_height(change_border(Div(Header("Guesses:", 6), guesses_str), 'solid'), '300px'), '40%'), #, {'style_border': 'solid'}
        SelectBox('mode', ['Easy', 'Intermediate', 'Hard']),
        Button("Play Again!", play_game),
        Button("Statistics", statistics)
    ])

@route
def win(state: State) -> Page:
    guesses_str = make_str(state.guesses)
    image_path = '/images_folder/'+image_list[state.lives]

    state.streak = True
    state.total_plays+=1
    state.wins+=1
    return Page(state, [
        "Congrats! You guessed the word:",
        bold(state.word),
        change_margin(float_right(change_height(Image(image_path), '300px')), '0px 200px'),
        change_width(change_height(change_border(Div(Header("Guesses:", 6), guesses_str), 'solid'), '300px'), '40%'), #, {'style_border': 'solid'}
        SelectBox('mode', ['Easy', 'Intermediate', 'Hard']),
        Button("Play Again!", play_game),
        Button("Statistics", statistics)
    ])

@route
def statistics(state: State, mode: str) -> Page:
    content = ["Play again to improve your score",
               "You have played "+str(state.total_plays)+" games",
               "You have won, "+str(state.wins)+" games",
                SelectBox('mode', ['Easy', 'Intermediate', 'Hard']),
               Button("Play Again!", play_game)
              ]
    if state.streak:
        content[0] = "You are on a roll!"
    if state.total_plays==1:
        content[1] = "You have played "+str(state.total_plays)+" game"
    if state.wins==1:
        content[2] = "You have won, "+str(state.wins)+" game"
    return Page(state, content)

start_server(State(7, [], "", [], 0, False, 0, ''))
