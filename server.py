from flask import Flask, render_template
from doc2vec import *
import sys

app = Flask(__name__)

@app.route("/")
def articles():
    """Show a list of article titles"""

    return render_template('articles.html', articles=articles)


@app.route("/article/<topic>/<filename>")
def article(topic, filename):
    """
    Show an article with relative path filename. Assumes the BBC structure of
    topic/filename.txt so our URLs follow that.
    """
    for item in articles:
        if item[0] == topic + '/' + filename:
            article = item
            break

    recommendation = recommended(article, articles, 5)
    return render_template('article.html', article=article, recommendation=recommendation)




# initialization
i = sys.argv.index('server:app')
glove_filename = sys.argv[i+1]
articles_dirname = sys.argv[i+2]

# glove_filename = sys.argv[1]
# articles_dirname = sys.argv[2]

gloves = load_glove(glove_filename)
articles = load_articles(articles_dirname, gloves)
