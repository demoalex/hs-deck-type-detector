#!/Users/fireharp/Documents/Prog/HS_AI/venv/bin/python
import re
import requests
from bs4 import BeautifulSoup

"""
By pro player
Thijs - http://www.hearthpwn.com/decks?filter-player=126
Savjz - http://www.hearthpwn.com/decks?filter-player=62

check scripts/hearthpwn/proplayers.csv

decks can be obtained by id only
"""

"""
http://www.hearthpwn.com/decks/708409
Deck Type: Ranked Deck
Deck Archetype: Control Warrior
Created: 12/22/2016 (Gadgetzan)
"""
url = 'http://www.hearthpwn.com/decks/708409'
r = requests.get(url)
with open('test.html', 'w') as output_file:
    text = r.text
    # output_file.write(text.encode('utf8'))

    soup = BeautifulSoup(text)
    card_finder = re.compile('rarity')
    deck_list = soup.find('aside').find_all('a', class_=card_finder)
    total = 0
    for card in deck_list:
        count = card.get('data-count')
        href = card.get('href')
        total += int(count)

    print 1
