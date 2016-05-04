#from subprocess import call
import sys
sys.path.append('../pagerank/')
pagerank = __import__('6_search.search')

def search(searchstring):

    return pagerank(searchstring)
