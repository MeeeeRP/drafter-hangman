from bakery import assert_equal
from drafter import *
from dataclasses import dataclass
import random

hide_debug_information()
set_website_title("Hangman!!!")
set_website_framed(False)


add_website_css("""
body {
    background-color: #99D9EA;
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
    words_per_mode: list[str]


def make_str(this_list: list[str]) -> str:
    this_str = ""
    for item in this_list:
        this_str+=item+" "
    return this_str

def get_lists(state: State, mode: str) -> list[str]:
    words_file = open('words.txt')
    words = [w.strip(' "') for w in words_file.read().split(',')]
    words_file.close()
    if mode=='Easy':
        easy = [word for word in words if len(word)<=5]
        print('easy assigned: '+str(len(easy)))
        return easy
    elif mode == 'Intermediate':
        medium = [word for word in words if len(word)>5 and len(word)<=8]
        return medium
    elif mode == 'Hard':
        hard = [word for word in words if len(word)>8]
        return hard
    else:
        return ["error"]
    
def get_word(state: State, mode: str) -> str:
    if not state.words_per_mode:
        return 'empty'
    if mode == "Easy":
        easy_num = random.randint(0,13981)
        word = state.words_per_mode[easy_num].upper()
    elif mode == "Intermediate":
        med_num = random.randint(0,69352)
        word = state.words_per_mode[med_num].upper()
    elif mode == "Hard":
        hard_num = random.randint(0, 94851)
        word = state.words_per_mode[hard_num].upper()
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
        change_background_color(Button("Submit", make_guess), 'white')
    ])


@route
def play_game(state: State, mode:str) -> Page:
    print('play_game run')
    state.mode=mode
    state.lives = 7
    state.guesses = []
    state.words_per_mode = get_lists(state, mode)
    state.word = get_word(state, mode)
    print(state.word)
    state.progress = []
    for letter in state.word:
        state.progress.append('_')
    state.words_per_mode = []
    return home(state)


@route
def index(state: State) -> Page:
    """
    Splash screen
    """
    return Page(state, [
        change_width(SelectBox('mode', ['Easy', 'Intermediate', 'Hard']), '10%'),
        float_right(change_background_color(change_width(Button("Play Game!", play_game), '80%'), 'white')),
        change_width(Image('splash_screen.jpg'), '100%')
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
        change_background_color(Button("Play Again!", play_game), 'white'),
        change_background_color(Button("Statistics", statistics), 'white')
    ])

@route
def win(state: State) -> Page:
    guesses_str = make_str(state.guesses)
    image_path = image_list[state.lives]

    state.streak = True
    state.total_plays+=1
    state.wins+=1
    return Page(state, [
        "Congrats! You guessed the word:",
        bold(state.word),
        change_margin(float_right(change_height(Image(image_path), '300px')), '0px 200px'),
        change_width(change_height(change_border(Div(Header("Guesses:", 6), guesses_str), 'solid'), '300px'), '40%'), #, {'style_border': 'solid'}
        SelectBox('mode', ['Easy', 'Intermediate', 'Hard']),
        change_background_color(Button("Play Again!", play_game), 'white'),
        change_background_color(Button("Statistics", statistics), 'white')
    ])

@route
def statistics(state: State, mode: str) -> Page:
    content = ["Play again to improve your score",
               "You have played "+str(state.total_plays)+" games",
               "You have won, "+str(state.wins)+" games",
                SelectBox('mode', ['Easy', 'Intermediate', 'Hard']),
               change_background_color(Button("Play Again!", play_game), 'white')
              ]
    if state.streak:
        content[0] = "You are on a roll!"
    if state.total_plays==1:
        content[1] = "You have played "+str(state.total_plays)+" game"
    if state.wins==1:
        content[2] = "You have won, "+str(state.wins)+" game"
    return Page(state, content)

start_server(State(7, [], "", [], 0, False, 0, '', []))

assert_equal(
 make_guess(State(lives=6, guesses=['A', 'E', 'I', 'O', 'S', 'M', 'P'], word='IMPOSTER', progress=['I', 'M', 'P', 'O', 'S', '_', 'E', '_'], wins=1, streak=False, total_plays=2, mode='Intermediate', words_per_mode=[]), 'b'),
 Page(state=State(lives=5,
                 guesses=['A', 'E', 'I', 'O', 'S', 'M', 'P', 'B'],
                 word='IMPOSTER',
                 progress=['I', 'M', 'P', 'O', 'S', '_', 'E', '_'],
                 wins=1,
                 streak=False,
                 total_plays=2,
                 mode='Intermediate',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='neck.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A E I O S M P B ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=4, guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P'], word='KVETCHING', progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 'p'),
 Page(state=State(lives=4,
                 guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P'],
                 word='KVETCHING',
                 progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='leftarm.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I N G K A T B P ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=7, guesses=['A', 'B', 'I'], word='BIAS', progress=['B', 'I', 'A', '_'], wins=0, streak=False, total_plays=0, mode='Easy', words_per_mode=[]), 's'),
 Page(state=State(lives=7,
                 guesses=['A', 'B', 'I', 'S'],
                 word='BIAS',
                 progress=['B', 'I', 'A', 'S'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Easy',
                 words_per_mode=[]),
     content=['Congrats! You guessed the word:',
              ,
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A B I S ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              SelectBox(name='mode', options=['Easy', 'Intermediate', 'Hard'], default_value=''),
              Button(text='Play Again!', url='/play_game'),
              Button(text='Statistics', url='/statistics')]))

assert_equal(
 play_game(State(lives=7, guesses=[], word='', progress=[], wins=0, streak=False, total_plays=0, mode='', words_per_mode=[]), 'Easy'),
 Page(state=State(lives=7,
                 guesses=[],
                 word='BIAS',
                 progress=['_', '_', '_', '_'],
                 wins=0,
                 streak=False,
                 total_plays=0,
                 mode='Easy',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), '', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=7, guesses=['A', 'B'], word='BIAS', progress=['B', '_', 'A', '_'], wins=0, streak=False, total_plays=0, mode='Easy', words_per_mode=[]), 'i'),
 Page(state=State(lives=7,
                 guesses=['A', 'B', 'I'],
                 word='BIAS',
                 progress=['B', 'I', 'A', '_'],
                 wins=0,
                 streak=False,
                 total_plays=0,
                 mode='Easy',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A B I ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 play_game(State(lives=0, guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P', 'S', 'L', 'W', 'Q'], word='KVETCHING', progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'], wins=1, streak=False, total_plays=2, mode='Hard', words_per_mode=[]), 'Intermediate'),
 Page(state=State(lives=7,
                 guesses=[],
                 word='IMPOSTER',
                 progress=['_', '_', '_', '_', '_', '_', '_', '_'],
                 wins=1,
                 streak=False,
                 total_plays=2,
                 mode='Intermediate',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), '', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 statistics(State(lives=0, guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P', 'S', 'L', 'W', 'Q'], word='KVETCHING', progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'], wins=1, streak=False, total_plays=2, mode='Hard', words_per_mode=[]), 'Easy'),
 Page(state=State(lives=0,
                 guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P', 'S', 'L', 'W', 'Q'],
                 word='KVETCHING',
                 progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'],
                 wins=1,
                 streak=False,
                 total_plays=2,
                 mode='Hard',
                 words_per_mode=[]),
     content=['Play again to improve your score',
              'You have played 2 games',
              'You have won, 1 game',
              SelectBox(name='mode', options=['Easy', 'Intermediate', 'Hard'], default_value=''),
              Button(text='Play Again!', url='/play_game')]))

assert_equal(
 make_guess(State(lives=6, guesses=['A', 'E', 'I'], word='IMPOSTER', progress=['I', '_', '_', '_', '_', '_', 'E', '_'], wins=1, streak=False, total_plays=2, mode='Intermediate', words_per_mode=[]), 'o'),
 Page(state=State(lives=6,
                 guesses=['A', 'E', 'I', 'O'],
                 word='IMPOSTER',
                 progress=['I', '_', '_', 'O', '_', '_', 'E', '_'],
                 wins=1,
                 streak=False,
                 total_plays=2,
                 mode='Intermediate',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='head.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A E I O ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=7, guesses=['I', 'N', 'G'], word='KVETCHING', progress=['_', '_', '_', '_', '_', '_', 'I', 'N', 'G'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 'k'),
 Page(state=State(lives=7,
                 guesses=['I', 'N', 'G', 'K'],
                 word='KVETCHING',
                 progress=['K', '_', '_', '_', '_', '_', 'I', 'N', 'G'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I N G K ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=3, guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P', 'S'], word='KVETCHING', progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 'l'),
 Page(state=State(lives=2,
                 guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P', 'S', 'L'],
                 word='KVETCHING',
                 progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='back.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I N G K A T B P S L ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=7, guesses=['I'], word='KVETCHING', progress=['_', '_', '_', '_', '_', '_', 'I', '_', '_'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 'n'),
 Page(state=State(lives=7,
                 guesses=['I', 'N'],
                 word='KVETCHING',
                 progress=['_', '_', '_', '_', '_', '_', 'I', 'N', '_'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I N ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=6, guesses=['I', 'N', 'G', 'K', 'A'], word='KVETCHING', progress=['K', '_', '_', '_', '_', '_', 'I', 'N', 'G'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 't'),
 Page(state=State(lives=6,
                 guesses=['I', 'N', 'G', 'K', 'A', 'T'],
                 word='KVETCHING',
                 progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='head.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I N G K A T ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 play_game(State(lives=5, guesses=['A', 'E', 'I', 'O', 'S', 'M', 'P', 'B', 'T', 'R'], word='IMPOSTER', progress=['I', 'M', 'P', 'O', 'S', 'T', 'E', 'R'], wins=2, streak=True, total_plays=3, mode='Intermediate', words_per_mode=[]), 'Easy'),
 Page(state=State(lives=7,
                 guesses=[],
                 word='GRANA',
                 progress=['_', '_', '_', '_', '_'],
                 wins=2,
                 streak=True,
                 total_plays=3,
                 mode='Easy',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), '', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=7, guesses=[], word='IMPOSTER', progress=['_', '_', '_', '_', '_', '_', '_', '_'], wins=1, streak=False, total_plays=2, mode='Intermediate', words_per_mode=[]), 'a'),
 Page(state=State(lives=6,
                 guesses=['A'],
                 word='IMPOSTER',
                 progress=['_', '_', '_', '_', '_', '_', '_', '_'],
                 wins=1,
                 streak=False,
                 total_plays=2,
                 mode='Intermediate',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='head.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=7, guesses=['I', 'N', 'G', 'K'], word='KVETCHING', progress=['K', '_', '_', '_', '_', '_', 'I', 'N', 'G'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 'a'),
 Page(state=State(lives=6,
                 guesses=['I', 'N', 'G', 'K', 'A'],
                 word='KVETCHING',
                 progress=['K', '_', '_', '_', '_', '_', 'I', 'N', 'G'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='head.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I N G K A ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=6, guesses=['A', 'E', 'I', 'O'], word='IMPOSTER', progress=['I', '_', '_', 'O', '_', '_', 'E', '_'], wins=1, streak=False, total_plays=2, mode='Intermediate', words_per_mode=[]), 's'),
 Page(state=State(lives=6,
                 guesses=['A', 'E', 'I', 'O', 'S'],
                 word='IMPOSTER',
                 progress=['I', '_', '_', 'O', 'S', '_', 'E', '_'],
                 wins=1,
                 streak=False,
                 total_plays=2,
                 mode='Intermediate',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='head.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A E I O S ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 statistics(State(lives=7, guesses=['A', 'B', 'I', 'S'], word='BIAS', progress=['B', 'I', 'A', 'S'], wins=1, streak=True, total_plays=1, mode='Easy', words_per_mode=[]), 'Easy'),
 Page(state=State(lives=7,
                 guesses=['A', 'B', 'I', 'S'],
                 word='BIAS',
                 progress=['B', 'I', 'A', 'S'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Easy',
                 words_per_mode=[]),
     content=['You are on a roll!',
              'You have played 1 game',
              'You have won, 1 game',
              SelectBox(name='mode', options=['Easy', 'Intermediate', 'Hard'], default_value=''),
              Button(text='Play Again!', url='/play_game')]))

assert_equal(
 make_guess(State(lives=7, guesses=[], word='BIAS', progress=['_', '_', '_', '_'], wins=0, streak=False, total_plays=0, mode='Easy', words_per_mode=[]), 'a'),
 Page(state=State(lives=7,
                 guesses=['A'],
                 word='BIAS',
                 progress=['_', '_', 'A', '_'],
                 wins=0,
                 streak=False,
                 total_plays=0,
                 mode='Easy',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=5, guesses=['A', 'E', 'I', 'O', 'S', 'M', 'P', 'B'], word='IMPOSTER', progress=['I', 'M', 'P', 'O', 'S', '_', 'E', '_'], wins=1, streak=False, total_plays=2, mode='Intermediate', words_per_mode=[]), 't'),
 Page(state=State(lives=5,
                 guesses=['A', 'E', 'I', 'O', 'S', 'M', 'P', 'B', 'T'],
                 word='IMPOSTER',
                 progress=['I', 'M', 'P', 'O', 'S', 'T', 'E', '_'],
                 wins=1,
                 streak=False,
                 total_plays=2,
                 mode='Intermediate',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='neck.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A E I O S M P B T ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=7, guesses=['I', 'N'], word='KVETCHING', progress=['_', '_', '_', '_', '_', '_', 'I', 'N', '_'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 'g'),
 Page(state=State(lives=7,
                 guesses=['I', 'N', 'G'],
                 word='KVETCHING',
                 progress=['_', '_', '_', '_', '_', '_', 'I', 'N', 'G'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I N G ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 play_game(State(lives=7, guesses=['A', 'B', 'I', 'S'], word='BIAS', progress=['B', 'I', 'A', 'S'], wins=1, streak=True, total_plays=1, mode='Easy', words_per_mode=[]), 'Hard'),
 Page(state=State(lives=7,
                 guesses=[],
                 word='KVETCHING',
                 progress=['_', '_', '_', '_', '_', '_', '_', '_', '_'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), '', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=4, guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P'], word='KVETCHING', progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 'p'),
 Page(state=State(lives=4,
                 guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P'],
                 word='KVETCHING',
                 progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='leftarm.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I N G K A T B P ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=2, guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P', 'S', 'L'], word='KVETCHING', progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 'w'),
 Page(state=State(lives=1,
                 guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P', 'S', 'L', 'W'],
                 word='KVETCHING',
                 progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='leftleg.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I N G K A T B P S L W ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=5, guesses=['A', 'E', 'I', 'O', 'S', 'M', 'P', 'B', 'T'], word='IMPOSTER', progress=['I', 'M', 'P', 'O', 'S', 'T', 'E', '_'], wins=1, streak=False, total_plays=2, mode='Intermediate', words_per_mode=[]), 'r'),
 Page(state=State(lives=5,
                 guesses=['A', 'E', 'I', 'O', 'S', 'M', 'P', 'B', 'T', 'R'],
                 word='IMPOSTER',
                 progress=['I', 'M', 'P', 'O', 'S', 'T', 'E', 'R'],
                 wins=2,
                 streak=True,
                 total_plays=3,
                 mode='Intermediate',
                 words_per_mode=[]),
     content=['Congrats! You guessed the word:',
              ,
              Image(url='neck.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A E I O S M P B T R ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              SelectBox(name='mode', options=['Easy', 'Intermediate', 'Hard'], default_value=''),
              Button(text='Play Again!', url='/play_game'),
              Button(text='Statistics', url='/statistics')]))

assert_equal(
 make_guess(State(lives=6, guesses=['A'], word='IMPOSTER', progress=['_', '_', '_', '_', '_', '_', '_', '_'], wins=1, streak=False, total_plays=2, mode='Intermediate', words_per_mode=[]), 'e'),
 Page(state=State(lives=6,
                 guesses=['A', 'E'],
                 word='IMPOSTER',
                 progress=['_', '_', '_', '_', '_', '_', 'E', '_'],
                 wins=1,
                 streak=False,
                 total_plays=2,
                 mode='Intermediate',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='head.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A E ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=7, guesses=[], word='KVETCHING', progress=['_', '_', '_', '_', '_', '_', '_', '_', '_'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 'i'),
 Page(state=State(lives=7,
                 guesses=['I'],
                 word='KVETCHING',
                 progress=['_', '_', '_', '_', '_', '_', 'I', '_', '_'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 index(State(lives=7, guesses=[], word='', progress=[], wins=0, streak=False, total_plays=0, mode='', words_per_mode=[])),
 Page(state=State(lives=7,
                 guesses=[],
                 word='',
                 progress=[],
                 wins=0,
                 streak=False,
                 total_plays=0,
                 mode='',
                 words_per_mode=[]),
     content=[SelectBox(name='mode', options=['Easy', 'Intermediate', 'Hard'], default_value=''),
              Button(text='Play Game!', url='/play_game'),
              Image(url='splash_screen.jpg', width=None, height=None)]))

assert_equal(
 make_guess(State(lives=6, guesses=['I', 'N', 'G', 'K', 'A', 'T'], word='KVETCHING', progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 'b'),
 Page(state=State(lives=5,
                 guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B'],
                 word='KVETCHING',
                 progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='neck.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I N G K A T B ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=6, guesses=['A', 'E', 'I', 'O', 'S'], word='IMPOSTER', progress=['I', '_', '_', 'O', 'S', '_', 'E', '_'], wins=1, streak=False, total_plays=2, mode='Intermediate', words_per_mode=[]), 'm'),
 Page(state=State(lives=6,
                 guesses=['A', 'E', 'I', 'O', 'S', 'M'],
                 word='IMPOSTER',
                 progress=['I', 'M', '_', 'O', 'S', '_', 'E', '_'],
                 wins=1,
                 streak=False,
                 total_plays=2,
                 mode='Intermediate',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='head.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A E I O S M ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=5, guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B'], word='KVETCHING', progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 'p'),
 Page(state=State(lives=4,
                 guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P'],
                 word='KVETCHING',
                 progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='leftarm.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I N G K A T B P ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=6, guesses=['A', 'E'], word='IMPOSTER', progress=['_', '_', '_', '_', '_', '_', 'E', '_'], wins=1, streak=False, total_plays=2, mode='Intermediate', words_per_mode=[]), 'i'),
 Page(state=State(lives=6,
                 guesses=['A', 'E', 'I'],
                 word='IMPOSTER',
                 progress=['I', '_', '_', '_', '_', '_', 'E', '_'],
                 wins=1,
                 streak=False,
                 total_plays=2,
                 mode='Intermediate',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='head.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A E I ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=1, guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P', 'S', 'L', 'W'], word='KVETCHING', progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 'q'),
 Page(state=State(lives=0,
                 guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P', 'S', 'L', 'W', 'Q'],
                 word='KVETCHING',
                 progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'],
                 wins=1,
                 streak=False,
                 total_plays=2,
                 mode='Hard',
                 words_per_mode=[]),
     content=['The word was KVETCHING',
              'K _ _ T _ _ I N G ',
              Image(url='rightleg.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I N G K A T B P S L W Q ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              SelectBox(name='mode', options=['Easy', 'Intermediate', 'Hard'], default_value=''),
              Button(text='Play Again!', url='/play_game'),
              Button(text='Statistics', url='/statistics')]))

assert_equal(
 make_guess(State(lives=7, guesses=['A'], word='BIAS', progress=['_', '_', 'A', '_'], wins=0, streak=False, total_plays=0, mode='Easy', words_per_mode=[]), 'b'),
 Page(state=State(lives=7,
                 guesses=['A', 'B'],
                 word='BIAS',
                 progress=['B', '_', 'A', '_'],
                 wins=0,
                 streak=False,
                 total_plays=0,
                 mode='Easy',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A B ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=6, guesses=['A', 'E', 'I', 'O', 'S', 'M'], word='IMPOSTER', progress=['I', 'M', '_', 'O', 'S', '_', 'E', '_'], wins=1, streak=False, total_plays=2, mode='Intermediate', words_per_mode=[]), 'p'),
 Page(state=State(lives=6,
                 guesses=['A', 'E', 'I', 'O', 'S', 'M', 'P'],
                 word='IMPOSTER',
                 progress=['I', 'M', 'P', 'O', 'S', '_', 'E', '_'],
                 wins=1,
                 streak=False,
                 total_plays=2,
                 mode='Intermediate',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='head.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A E I O S M P ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 make_guess(State(lives=4, guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P'], word='KVETCHING', progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'], wins=1, streak=True, total_plays=1, mode='Hard', words_per_mode=[]), 's'),
 Page(state=State(lives=3,
                 guesses=['I', 'N', 'G', 'K', 'A', 'T', 'B', 'P', 'S'],
                 word='KVETCHING',
                 progress=['K', '_', '_', 'T', '_', '_', 'I', 'N', 'G'],
                 wins=1,
                 streak=True,
                 total_plays=1,
                 mode='Hard',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              ,
              Image(url='rightarm.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'I N G K A T B P S ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))
