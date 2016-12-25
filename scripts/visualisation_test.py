import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
from sklearn.manifold import TSNE


def load_decks_data():
    arr = []
    try:
        con = sqlite3.connect('data/hearthpwn/decks.db')
        deck_cur = con.cursor()
        cards_cur = con.cursor()

        for row in deck_cur.execute('SELECT id FROM decks'):
            deck_id = row[0]
            deck = []
            for r in cards_cur.execute('SELECT card_id, count FROM cards_in_decks WHERE deck_id=%d' % deck_id):
                count = r[1]
                for i in xrange(count):
                    deck.append(r[0])
            deck.sort()
            arr.append(deck)


    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()

    return np.array(arr)

X = load_decks_data()
# fig = plt.figure(figsize=(15, 8))
tsne = TSNE(n_components=2, random_state=0)
Y = tsne.fit_transform(X)
ax = plt.plot()
plt.scatter(Y[:, 0], Y[:, 1], c='red', cmap=plt.cm.Spectral)
# ax.xaxis.set_major_formatter(NullFormatter())
# ax.yaxis.set_major_formatter(NullFormatter())
plt.axis('tight')

plt.show()
