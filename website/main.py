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
    """
    Converts list[str] to string with ' ' in between elements
    
    Returns:
        str: converted list as str
    """
    this_str = ""
    for item in this_list:
        this_str+=item+" "
    return this_str

def get_lists(state: State, mode: str) -> list[str]:
    """
    Pulls words list from words.txt and filters by length
    
    **Not unit tested because the lists it returns are so long it would slow down my page**
    Args:
        mode (str): difficulty of game; 'Easy', 'Intermediate', or 'Hard'
         
    Returns:
        list[str]: filtered list based on difficulty
    """
    words_file = open('words.txt')
    words = [w.strip(' "') for w in words_file.read().split(',')]
    words_file.close()
    if mode=='Easy':
        easy = [word for word in words if len(word)<=5]
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
    """
    Chooses random word from filtered list of words
    
    **Not unit tested because randomized**

    Args:
        mode (str): difficulty of game; 'Easy', 'Intermediate', or 'Hard'
         
    Returns:
        str: word from chosen list        
    """
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
    """
    Called when a new round is started:
        resets short-term stats
        calls function to get lists (static.words_per_mode) and chooses word
        sets static.words_per_mode to [] so that state is not incredibly large
    
    Args:
        mode (str): difficulty of game; 'Easy', 'Intermediate', or 'Hard'
    """
    state.mode=mode
    state.lives = 7
    state.guesses = []
    state.words_per_mode = get_lists(state, mode)
    state.word = get_word(state, mode)
    state.progress = []
    for letter in state.word:
        state.progress.append('_')
    state.words_per_mode = []
    return home(state)


@route
def index(state: State) -> Page:
    """
    Splash/Title screen
    """
    return Page(state, [
        change_width(SelectBox('mode', ['Easy', 'Intermediate', 'Hard']), '10%'),
        float_right(change_background_color(change_width(Button("Play Game!", play_game), '80%'), 'white')),
        change_width(Image('splash_screen.jpg'), '100%')
        ])

@route
def make_guess(state: State, guess: str) -> Page:
    """
    Checks that guess is letter and single character
    Tests whether guess is in word and appends to state.guesses
    
    Args:
        guess (str): guess made by user
    
    Returns:
        function: correct_guess or wrong_guess
    """
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
    """
    Decreases lives and checks for loss case
    """
    state.lives -= 1
    if state.lives > 0:
        return home(state)
    return loss(state)

@route
def correct_guess(state: State, guess) -> Page:
    """
    Replaces all instances of the letter in state.progress based on index word
    
    Args:
        guess (str): guess made by user
        
    Returns:
        function: home() if word not guessed else win()
    """
    for i, letter in enumerate(state.word):
        if guess.upper() == letter:
            state.progress[i]=letter
    progress_str = make_str(state.progress)
    if "_" in progress_str:
        return home(state)
    return win(state)


@route
def loss(state: State) -> Page:
    """
    Displays hangman image, guesses, correct word, and statistics page
    Alters statistics
    """
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
    """
    Displays hangman image, guesses, correct word, and statistics page
    Alters statistics
    """
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
    """
    Displays positive or negative message depending on streak, total plays and total wins
    """
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

assert_equal(make_str(['_', '_', '_', '_']), '_ _ _ _ ')

assert_equal(
 win(State(lives=6, guesses=['A'], word='START', progress=['_', '_', 'A', '_', '_'], wins=0, streak=False, total_plays=1, mode='Easy', words_per_mode=[])),
 Page(state=State(lives=6,
                 guesses=['A'],
                 word='START',
                 progress=['_', '_', 'A', '_', '_'],
                 wins=1,
                 streak=True,
                 total_plays=2,
                 mode='Easy',
                 words_per_mode=[]),
     content=['Congrats! You guessed the word:',
              'START',
              Image(url='head.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              SelectBox(name='mode', options=['Easy', 'Intermediate', 'Hard'], default_value=''),
              Button(text='Play Again!', url='/play_game'),
              Button(text='Statistics', url='/statistics')]))

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
 play_game(State(lives=7, guesses=[], word='', progress=[], wins=0, streak=False, total_plays=0, mode='', words_per_mode=[]), 'Easy'),
 Page(state=State(lives=7,
                 guesses=[],
                 word='START',
                 progress=['_', '_', '_', '_', '_'],
                 wins=0,
                 streak=False,
                 total_plays=0,
                 mode='Easy',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              '_ _ _ _ _ ',
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), '', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 statistics(State(lives=6, guesses=['A'], word='START', progress=['_', '_', 'A', '_', '_'], wins=1, streak=True, total_plays=2, mode='Easy', words_per_mode=[]), 'Easy'),
 Page(state=State(lives=6,
                 guesses=['A'],
                 word='START',
                 progress=['_', '_', 'A', '_', '_'],
                 wins=1,
                 streak=True,
                 total_plays=2,
                 mode='Easy',
                 words_per_mode=[]),
     content=['You are on a roll!',
              'You have played 2 games',
              'You have won, 1 game',
              SelectBox(name='mode', options=['Easy', 'Intermediate', 'Hard'], default_value=''),
              Button(text='Play Again!', url='/play_game')]))

assert_equal(
 make_guess(State(lives=7, guesses=[], word='START', progress=['_', '_', '_', '_', '_'], wins=0, streak=False, total_plays=0, mode='Easy', words_per_mode=[]), 'a'),
 Page(state=State(lives=7,
                 guesses=['A'],
                 word='START',
                 progress=['_', '_', 'A', '_', '_'],
                 wins=0,
                 streak=False,
                 total_plays=0,
                 mode='Easy',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              '_ _ A _ _ ',
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 correct_guess(State(lives=6, guesses=['A'], word='START', progress=['_', '_', '_', '_', '_'], wins=0, streak=False, total_plays=0, mode='Easy', words_per_mode=[]), 't'),
 Page(state=State(lives=6,
                 guesses=['A'],
                 word='START',
                 progress=['_', 'T', '_', '_', 'T'],
                 wins=0,
                 streak=False,
                 total_plays=0,
                 mode='Easy',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              '_ T _ _ T ',
              Image(url='head.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 home(State(lives=7, guesses=['A'], word='START', progress=['_', '_', 'A', '_', '_'], wins=0, streak=False, total_plays=0, mode='Easy', words_per_mode=[])),
 Page(state=State(lives=7,
                 guesses=['A'],
                 word='START',
                 progress=['_', '_', 'A', '_', '_'],
                 wins=0,
                 streak=False,
                 total_plays=0,
                 mode='Easy',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              '_ _ A _ _ ',
              Image(url='empty.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))

assert_equal(
 loss(State(lives=6, guesses=['A'], word='START', progress=['_', '_', 'A', '_', '_'], wins=0, streak=False, total_plays=0, mode='Easy', words_per_mode=[])),
 Page(state=State(lives=6,
                 guesses=['A'],
                 word='START',
                 progress=['_', '_', 'A', '_', '_'],
                 wins=0,
                 streak=False,
                 total_plays=1,
                 mode='Easy',
                 words_per_mode=[]),
     content=['The word was START',
              '_ _ A _ _ ',
              Image(url='rightleg.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              SelectBox(name='mode', options=['Easy', 'Intermediate', 'Hard'], default_value=''),
              Button(text='Play Again!', url='/play_game'),
              Button(text='Statistics', url='/statistics')]))

assert_equal(
 wrong_guess(State(lives=7, guesses=['A'], word='START', progress=['_', '_', 'A', '_', '_'], wins=0, streak=False, total_plays=0, mode='Easy', words_per_mode=[])),
 Page(state=State(lives=6,
                 guesses=['A'],
                 word='START',
                 progress=['_', '_', 'A', '_', '_'],
                 wins=0,
                 streak=False,
                 total_plays=0,
                 mode='Easy',
                 words_per_mode=[]),
     content=["Let's play Hangman!!",
              '_ _ A _ _ ',
              Image(url='head.png', width=None, height=None),
              Div(Header(body='Guesses:', level=6), 'A ', {'style_border': 'solid', 'style_height': '300px', 'style_width': '40%'}),
              TextBox(name='guess', kind='text', default_value=''),
              Button(text='Submit', url='/make_guess')]))
