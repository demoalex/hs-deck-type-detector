#!../venv/bin/python
# coding=utf-8
"""
.. module:: hearthpwn_scraper.py
   :synopsis: Hearthpwn scraping functions.

.. moduleauthor:: Alex Yanitskiy <demo.alex@gmail.com>


"""
import sys
import sqlite3
import re
import csv
import requests
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


def get_decks_listings_by_query(session=None, player=None, patch=None, class_=None, format_=None, sort=None):
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
        arr = get_decks_listings_by_query(s, i+1, 31, 1024, 1, '-viewcount')
        with open("scripts/hearthpwn/output.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerows(arr)
        print "User %s is processed" % (i+1)


def get_deck_by_url(url, session=None, verbose=None):
    req = session.get(url) if session else requests.get(url)

    html = req.text

    soup = BeautifulSoup(html)
    card_finder = re.compile('rarity')
    card_listing = soup.find('aside')
    deck_list = card_listing.find_all('a', class_=card_finder)
    cost_list = card_listing.find_all('td', class_='col-cost')
    total = 0

    titles = ['href', 'count', 'cost']
    processed_card_arr = []
    for card in zip(deck_list, cost_list):
        count = card[0].get('data-count')
        href = card[0].get('href')
        cost = card[1].getText()
        processed_card_arr.append([href, count, cost])
        total += int(count)

    if verbose is not None:
        print "Deck %s parsed: " % url
        row_format = "{:>45}" + "{:>15}" * (len(titles)-1)
        print row_format.format(*titles)
        for row in processed_card_arr:
            print row_format.format(*row)

    return processed_card_arr


def scrape_decks_from_csv():
    """

    :return:
    """

    get_deck_by_url('http://www.hearthpwn.com/decks/700814-thijsnl-build-a-wall', verbose=1)

    try:
        con = sqlite3.connect('data/hearthpwn/decks.db')

        cur = con.cursor()
        cur.execute('SELECT SQLITE_VERSION()')

        data = cur.fetchone()

        print "SQLite version: %s" % data

    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        if con:
            con.close()


#scrape_warrior_pro_players_gadgetzan()
#scrape_decks_from_csv()
