#!../venv/bin/python
# coding=utf-8
"""
.. module:: hearthpwn_scraper.py
   :synopsis: Hearthpwn scraping functions.

.. moduleauthor:: Alex Yanitskiy <demo.alex@gmail.com>


"""
import sys
import random
import sqlite3
import re
import csv
import requests
import time
from bs4 import BeautifulSoup


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


def get_decks_listings_by_query(session=None, player=None, patch=None, class_=None, format_=None, sort=None, page=None):
    """
    TODO: we should map human readable params to hearthpwn values(should we?)

    :param player: int, player id from scripts/hearthpwn/proplayers.csv
    :param patch: int, Gadgetzan
    :param class_: int, Warrior
    :param format: int, Standard
    :param sort: sorting
    :param page: int, sorting
    :return:
    """
    url = 'http://www.hearthpwn.com/decks?filter-build=%s&filter-class=%s&filter-deck-tag=1&filter-show-standard=%s&sort=%s' % (patch, class_, format_, sort)
    if page is not None:
        url += '&page=%d' % page
    if player is not None:
        url += '&filter-player=%d' % player
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

    :return: nothing
    """
    s = requests.Session()
    # this session pre-heating is required, otherwise all filters are dropped
    # we don't know why this happens to hearthpwn, but it does. so let's just use it this way
    s.get('http://www.hearthpwn.com/decks?filter-build=31&filter-class=1024')
    lst = list(range(427))
    random.shuffle(lst)  # try to shuffle ids to get better parsing results
    for i in lst:
        arr = get_decks_listings_by_query(s, i+1, 31, 1024, 1, '-viewcount')
        with open("scripts/hearthpwn/output.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerows(arr)
        time.sleep(1)  # try to sleep not to get same results from server
        print "User %s is processed" % (i+1)


def scrape_warrior_all_players_gadgetzan():
    """
    scrape all decks based on: Gadgetzan, Warrior

    request / querystring
    http://www.hearthpwn.com/decks?filter-build=31&filter-class=1024&filter-deck-tag=1&filter-show-standard=1&sort=-viewcount&page=XXX

    59 pages here

    :return: nothing
    """
    s = requests.Session()
    # this session pre-heating is required, otherwise all filters are dropped
    # we don't know why this happens to hearthpwn, but it does. so let's just use it this way
    s.get('http://www.hearthpwn.com/decks?filter-build=31&filter-class=1024')
    lst = list(range(59))
    random.shuffle(lst)  # try to shuffle pages to get better parsing results
    for i in lst:
        arr = get_decks_listings_by_query(s, None, 31, 1024, 1, '-viewcount', i+1)
        with open("scripts/hearthpwn/output.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerows(arr)
        time.sleep(1)  # try to sleep not to get same results from server
        print "Page %d is processed" % (i+1)


def get_deck_by_url(url, session=None, verbose=None):
    """

    :param url: should be full url address, not relative
    :param session: if not set – simple request is used
    :param verbose:
    :return: returns tuple:

        deck as list of cards, where each card is also a list: [href, count, cost]

        total cards count (we usually don't want decks with less than 30 cards)
    """
    req = session.get(url) if session else requests.get(url)

    html = req.text

    soup = BeautifulSoup(html)
    card_finder = re.compile('rarity')
    card_listing = soup.find('aside')
    if card_listing is None:
        return [], 0
    deck_list = card_listing.find_all('a', class_=card_finder)
    cost_list = card_listing.find_all('td', class_='col-cost')
    total = 0

    titles = ['href', 'count', 'cost']
    processed_card_arr = []
    for card in zip(deck_list, cost_list):
        count = int(card[0].get('data-count'))
        href = card[0].get('href')
        cost = int(card[1].getText())
        processed_card_arr.append([href, count, cost])
        total += count

    if verbose is not None:
        print "Deck %s (cards total num: %d) parsed: " % (url, total)
        row_format = "{:>45}" + "{:>15}" * (len(titles)-1)
        print row_format.format(*titles)
        for row in processed_card_arr:
            print row_format.format(*row)

    return processed_card_arr, total


def scrape_decks_from_csv(csv_file):
    """

    :return: nothing
    """

    with open(csv_file, 'rb') as decks_file:
        reader = csv.reader(decks_file)
        decks = list(reader)

    s = requests.Session()
    for deck in decks:
        try:
            con = sqlite3.connect('data/hearthpwn/decks.db')
            cur = con.cursor()
            deck_id = None
            for r in cur.execute('SELECT id FROM decks WHERE href="%s"' % deck[0]):
                deck_id = r[0]
            if deck_id is None:  # parse only decks we don't have in db
                d = get_deck_by_url('http://www.hearthpwn.com' + deck[0], session=s, verbose=1)
                if d[1] == 30:
                    cur.execute('INSERT INTO decks (href, class, format) VALUES ("%s", 1, 1)' % deck[0])
                    deck_id = cur.lastrowid
                    for card in d[0]:
                        cur.execute('INSERT OR IGNORE INTO cards (href, cost) VALUES ("%s", %d)' % (card[0], card[2]))
                        for r in cur.execute('SELECT id FROM cards WHERE href="%s"' % card[0]):
                            card_id = r[0]
                        cur.execute('INSERT INTO cards_in_decks(deck_id, card_id, count) VALUES (%d, %d, %d)' %
                                    (deck_id, card_id, card[1]))
            con.commit()
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
            # sys.exit(1)
        finally:
            if con:
                con.close()


# scrape_warrior_pro_players_gadgetzan()
# scrape_warrior_all_players_gadgetzan()
# scrape_decks_from_csv('data/hearthpwn/pro_players_warrior_gadgetzan.csv')
scrape_decks_from_csv('data/hearthpwn/all_players_warrior_gadgetzan.csv')
