import happybase
import sys
import json
import operator

from variables import MACHINE, VUID, PAGE_TABLE, INDEX_TABLE, COLUMN_FAMILY, COLUMN

## use row to get each row, go into each row, count up the results

'''
Get top K pages for given keyword search.

You must manage multiple keyword searches: [nfl], [air jordan]

You can get a row for a given keyword with: table.row(keyword)

Recall from 5 that the data is JSON formatted like:
    data = {
        'title': title,
        'word': word,
        'tfidf': tfidf,
        'pr': pr
    }
Which can be loaded with json.loads(data)

Calculate a score per page with: tf-idf + W * page_rank

If there are multiple keywords, add the scores for each keyword.

Note that the every keyword must occur in a given page to be in the result.
'''
def search(keywords):
    print 'Searching for %s' % keywords
    W = 4
    TOP_K = 10

    connection = happybase.Connection(MACHINE + '.vampire', table_prefix=VUID)
    table = connection.table(INDEX_TABLE)
    rows = table.rows(keywords)
    ts = {}
    for key, data in rows:
        for element in data.values():
            jdata = json.loads(element)

            tfidf = jdata["tfidf"]
            pr = jdata["pr"]
            title = jdata["title"]

            score = tfidf + W * pr

            if title in ts:
                # multiple keywords for this page
                ts[title] += score
            else:
                # first keyword for this page
                ts[title] = score

    pages = []
    for key, data in rows:
        key_pages = [json.loads(e)["title"] for e in data.values()]
        pages.append(key_pages)

    if not pages:
        return []

    common_pages = list(set(pages[0]).intersection(*pages))
    arr = []
    for page in common_pages:
        arr.append((ts[page], page))

    arr.sort(key=operator.itemgetter(0))
    return arr[::-1][:TOP_K]


if __name__ == '__main__':
    keywords = sys.argv[1:]
    print search(keywords)
