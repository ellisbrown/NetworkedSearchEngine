#from subprocess import call
import sys
import wikipedia
import json
#sys.path.append('../makeHBase/')
#pagerank = __import__('../search')
from subprocess import Popen, PIPE
from search import get_results

def get_wiki_link(title):
    wikipedia.set_lang("en")
    page = wikipedia.page(title)
    #summary = wikipedia.summary(page.title, sentences=1)
    return [page.title, page.url]


def search(searchstring):
    # results = pagerank.search(searchstring)
    # titles = [e[0] for e in results]
    # results = wikipedia.search(searchstring)
    # titles = [e for e in results]
    print 'running get_results'
    results = get_results(searchstring.split())
    titles = [e[0] for e in results]    

    print(titles)

    return "|".join([",".join(get_wiki_link(title)) for title in titles])


if __name__ == '__main__':
    keywords = sys.argv[1:]
    print search(keywords)
