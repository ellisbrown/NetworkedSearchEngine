#from subprocess import call
import sys
import wikipedia
import json
sys.path.append('../makeHBase/')
pagerank = __import__('6_search')

def get_wiki_link(title):
    page = wikipedia.page(title)
    summary = wikipedia.summary(page.title, sentences=1)
    return page.title, page.url. summary


def search(searchstring):
    results = pagerank.search(searchstring)
    titles = [e[0] for e in results]
    return [get_wiki_link(title) for title in titles]

if __name__ == '__main__':
    keywords = sys.argv[1:]
    print search(keywords)
