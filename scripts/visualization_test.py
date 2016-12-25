import sqlite3
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import mpld3
from sklearn.manifold import TSNE


class ClickInfo(mpld3.plugins.PluginBase):
    """mpld3 Plugin for getting info on click        """

    JAVASCRIPT = """
    mpld3.register_plugin("clickinfo", ClickInfo);
    ClickInfo.prototype = Object.create(mpld3.Plugin.prototype);
    ClickInfo.prototype.constructor = ClickInfo;
    ClickInfo.prototype.requiredProps = ["id", "urls"];
    function ClickInfo(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    ClickInfo.prototype.draw = function(){
        var obj = mpld3.get_element(this.props.id);
        urls = this.props.urls;
        obj.elements().on("mousedown",
                          function(d, i){
                            window.open(urls[i], '_blank')});
    }
    """

    def __init__(self, points, urls):
        self.points = points
        self.urls = urls
        if isinstance(points, matplotlib.lines.Line2D):
            suffix = "pts"
        else:
            suffix = None
        self.dict_ = {"type": "clickinfo",
                      "id": mpld3.utils.get_id(points, suffix),
                      "urls": urls}


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
    players = []
    hrefs = []
    try:
        con = sqlite3.connect('data/hearthpwn/decks.db')
        deck_cur = con.cursor()
        cards_cur = con.cursor()
        position_mapping = {}
        cost_mapping = {}

        cards_used = 25
        for row in cards_cur.execute('SELECT id, cost FROM cards'):
            position_mapping[row[0]] = cards_used
            cost_mapping[row[0]] = row[1]
            cards_used += 1

        for row in deck_cur.execute('SELECT id, player, href FROM decks'):
            deck_id = row[0]
            player = row[1]
            hrefs.append('http://www.hearthpwn.com' + row[2])
            deck = np.zeros(25 + cards_used)

            total_deck_value = 0
            for r in cards_cur.execute('SELECT card_id, count FROM cards_in_decks WHERE deck_id=%d' % deck_id):
                count = r[1]
                deck[position_mapping[r[0]]] = count
                deck[cost_mapping[r[0]]] = deck[cost_mapping[r[0]]] + count
                total_deck_value += count*cost_mapping[r[0]]
            deck[24] = total_deck_value
            arr.append(deck)
            players.append(player)


    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
    finally:
        if con:
            con.close()

    return np.array(arr), players, hrefs


X, players, links = load_decks_data_by_card_usage()
targets = []
labels = []
for link in links:
    html = '<div class="lbl">%s</div>' % link
    labels.append(html)
    targets.append(link)
# fig = plt.figure(figsize=(15, 8))
tsne = TSNE(n_components=2, random_state=0)
Y = tsne.fit_transform(X)
pro_Y = []
other_Y = []
pro_targets = []
other_targets = []
pro_labels = []
other_labels = []
for i, x in enumerate(X):
    if players[i] is not None:
        pro_Y.append(Y[i])
        pro_targets.append(targets[i])
        pro_labels.append(labels[i])
    else:
        other_Y.append(Y[i])
        other_targets.append(targets[i])
        other_labels.append(labels[i])
pro_Y = np.array(pro_Y)
other_Y = np.array(other_Y)
fig, ax = plt.subplots()
other_scatter = ax.scatter(other_Y[:, 0], other_Y[:, 1], c='lime')
pro_scatter = ax.scatter(pro_Y[:, 0], pro_Y[:, 1], c='red')
plt.axis('tight')

css = """
.lbl
{
  color: #ffffff;
  background-color: #000000;
}
"""
pro_tooltip = mpld3.plugins.PointHTMLTooltip(pro_scatter, labels=pro_labels, css=css)
other_tooltip = mpld3.plugins.PointHTMLTooltip(other_scatter, labels=other_labels, css=css)
pro_click = ClickInfo(pro_scatter, urls=pro_targets)
other_click = ClickInfo(other_scatter, urls=other_targets)
mpld3.plugins.connect(fig, pro_tooltip, pro_click, other_tooltip, other_click)

mpld3.show()
