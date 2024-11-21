import requests

response = requests.get('https://raw.githubusercontent.com/RazorSh4rk/random-word-api/refs/heads/master/words.json')

words = [w.strip(' "') for w in response.text.split(',')]

easy = [word for word in words if len(word)<=5]

medium = [word for word in words if len(word)>5 and len(word)<=8]

hard = [word for word in words if len(word)>8]
