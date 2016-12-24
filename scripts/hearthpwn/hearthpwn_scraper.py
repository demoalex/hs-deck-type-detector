#!../venv/bin/python
import re
import csv
import requests
from bs4 import BeautifulSoup

"""
By pro player
Thijs - http://www.hearthpwn.com/decks?filter-player=126
Savjz - http://www.hearthpwn.com/decks?filter-player=62

check scripts/hearthpwn/proplayers.csv

decks can be obtained by id only
"""


def sample_scrape():
    """
    just for debugging

    http://www.hearthpwn.com/decks/708409
    Deck Type: Ranked Deck
    Deck Archetype: Control Warrior
    Created: 12/22/2016 (Gadgetzan)
    """
    url = 'http://www.hearthpwn.com/decks/708409'
    req = requests.get(url)
    with open('test.html', 'w') as output_file:
        text = req.text
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


def parse_decks_listing(text):
    soup = BeautifulSoup(text)
    listing = soup.find('table', class_=re.compile('listing'))
    result = []
    if listing is not None:
        deck_finder = lambda tag: tag.name == 'span' and tag.get('class') == ['tip']
        decks = listing.find_all(deck_finder)
        for deck in decks:
            result.append([deck.find('a').get('href')])
    return result


def get_decks_by_query(session=None, player=None, patch=None, class_=None, format_=None, sort=None):
    """
    TODO: we should map human readable params to hearthpwn values(should we?)

    :param player: player id from scripts/hearthpwn/proplayers.csv
    :param patch: Gadgetzan
    :param class_: Warrior
    :param format: Standard
    :param sort: sorting
    :return:
    """
    url = 'http://www.hearthpwn.com/decks?filter-build=%s&filter-class=%s&filter-deck-tag=1&filter-player=%s&filter-show-standard=%s&sort=%s' % (patch, class_, player, format_, sort)
    req = session.get(url) if session else requests.get(url)
    text = req.text
    result = parse_decks_listing(text)
    return result


def scrape_warrior_pro_players_gadgetzan():
    """
    scrape all decks based on: Player!=null, Gadgetzan, Warrior

    request / querystring
    http://www.hearthpwn.com/filter-build=31&filter-class=1024&filter-deck-tag=1&filter-player=XXX&filter-show-standard=1&sort=-viewcount

    it's ok to get only first page for each player

    :return:
    """
    s = requests.Session()
    # this session pre-heating is required, otherwise all filters are dropped
    # we don't know why this happens to hearthpwn, but it does. so let's just use it this way
    s.get('http://www.hearthpwn.com/decks?filter-build=31&filter-class=1024')
    for i in xrange(427):
        arr = get_decks_by_query(s, i+1, 31, 1024, 1, '-viewcount')
        with open("scripts/hearthpwn/output.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerows(arr)
        print "User %s is processed" % (i+1)


scrape_warrior_pro_players_gadgetzan()
