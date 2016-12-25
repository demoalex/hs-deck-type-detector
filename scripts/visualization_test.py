import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
from sklearn.manifold import TSNE


def load_decks_data_by_card_id():
    arr = []
    colors = []
    try:
        con = sqlite3.connect('data/hearthpwn/decks.db')
        deck_cur = con.cursor()
        cards_cur = con.cursor()

        # for r in cards_cur.execute('SELECT id FROM cards WHERE deck_id=%d' % deck_id):
        #     count = r[1]
        #     for i in xrange(count):
        #         deck.append(r[0])
        #
        for row in deck_cur.execute('SELECT id, player FROM decks'):
            deck_id = row[0]
            color = 'green' if row[1] else 'red'
            deck = []
            for r in cards_cur.execute('SELECT card_id, count FROM cards_in_decks WHERE deck_id=%d' % deck_id):
                count = r[1]
                for i in xrange(count):
                    deck.append(r[0])
            deck.sort()
            arr.append(deck)
            colors.append(color)


    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()

    return np.array(arr), colors


def load_decks_data_by_card_usage():
    arr = []
    colors = []
    try:
        con = sqlite3.connect('data/hearthpwn/decks.db')
        deck_cur = con.cursor()
        cards_cur = con.cursor()
        position_mapping = {}

        cards_used = 0
        for row in cards_cur.execute('SELECT id FROM cards'):
            position_mapping[row[0]] = cards_used
            cards_used += 1

        for row in deck_cur.execute('SELECT id, player FROM decks'):
            deck_id = row[0]
            color = 'green' if row[1] else 'red'
            deck = np.zeros(cards_used)
            for r in cards_cur.execute('SELECT card_id, count FROM cards_in_decks WHERE deck_id=%d' % deck_id):
                count = r[1]
                deck[position_mapping[r[0]]] = count
            arr.append(deck)
            colors.append(color)


    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()

    return np.array(arr), colors


X, colors = load_decks_data_by_card_usage()
# fig = plt.figure(figsize=(15, 8))
tsne = TSNE(n_components=2, random_state=0)
Y = tsne.fit_transform(X)
pro_Y = []
other_Y = []
for i, x in enumerate(X):
    if colors[i] == 'red':
        pro_Y.append(Y[i])
    else:
        other_Y.append(Y[i])
pro_Y = np.array(pro_Y)
other_Y = np.array(other_Y)
ax = plt.plot()
plt.scatter(pro_Y[:, 0], pro_Y[:, 1], c='lime')
plt.scatter(other_Y[:, 0], other_Y[:, 1], c='red')
plt.axis('tight')

plt.show()
