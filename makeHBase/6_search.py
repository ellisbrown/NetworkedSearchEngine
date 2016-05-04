import happybase
import sys
import json
import operator

from variables import MACHINE, PAGE_TABLE, INDEX_TABLE, COLUMN_FAMILY, COLUMN


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
    W = 7
    TOP_K = 10

    connection = happybase.Connection('ec2-52-207-255-157.compute-1.amazonaws.com')
    #connection = happybase.Connection(MACHINE + '.vampire', table_prefix=VUID)
    table = connection.table(INDEX_TABLE)

    rows = table.rows(keywords)

    ts = {}

    for key, data in rows:
        for e in data.values():
            jdata = json.loads(e)

            tfidf = jdata["tfidf"]
            pr = jdata["pr"]
            title = jdata["title"]

            score = tfidf / 3 + W * pr

            #kiddie heuristics
            keys = " ".join(keywords).strip()

            if keys == title:
                score *= 100

            keywords = [word[:-1] if word[-1] == 's' else word for word in keywords]
            for word in keywords:
                if word in title:
                    score *= 10

            if title in ts:
                # multiple keywords for this page
                ts[title] += score
            else:
                # first keyword for this page
                ts[title] = score

    pages = []
    #could do scores and titles in one pass but I like this list comp

    for key, data in rows:
        key_pages = [json.loads(e)["title"] for e in data.values()]
        pages.append(key_pages)

    if not pages:
        return []

    common_pages = list(set(pages[0]).intersection(*pages))

    ret = []
    for page in common_pages:
        ret.append((page, ts[page]))

    ret.sort(key=operator.itemgetter(1))
    return ret[::-1][:10]

if __name__ == '__main__':
    keywords = sys.argv[1:]
    print search(keywords)
