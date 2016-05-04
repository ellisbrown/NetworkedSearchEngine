from pyspark import SparkConf, SparkContext

import happybase
import sys
import json

from variables import MACHINE, PAGE_TABLE, INDEX_TABLE, COLUMN_FAMILY, COLUMN

tf_idf_files = 's3://networks-final/tf_idf/*'
rank_files = 's3://networks-final/ranks/*'


'''
Store in hbase: word -> {'column_family:page_title': {'title': title, 'word': word, 'tfidf': tfidf, 'pr': pr}}

1. Create (title, ((title, word, tf-idf), page_rank)) -- this requires a join.
2. Group by word (will need a map before being able to group)
3. Foreach() group, write to hbase using the store function.
4. The the scan function in step 0 to check results.

Hbase put info:
http://happybase.readthedocs.org/en/latest/user.html#performing-batch-mutations

'''
def hbase(spark):
    tf_idf_lines = spark.textFile(tf_idf_files)
    tf_idfs = tf_idf_lines.map(lambda line: eval(line))
    # (title, word, tfidf)

    rank_lines = spark.textFile(rank_files)
    ranks = rank_lines.map(lambda line: eval(line))
    # (title, page_rank)

    # do something

    #1.
    # p1 = tf_idfs.keyBy(lambda (title, word, tfidf): title) \
    #     .join(ranks.keyBy(lambda (title, page_rank): title)) \
    #     .map(lambda (title, ((t1, word, tfidf), (t2, page_rank))): (title, ((title, word, tfidf), page_rank)))

    p1 = tf_idfs.keyBy(lambda (title, word, tfidf): title).join(ranks)

    #(word, (title,tfidf,pr) )
    #2.
    p2 = p1.map(lambda (title, ((t, word, tfidf), pr)):  (word, (title, tfidf, pr))).groupByKey()

    #3 (title, tfidf, pr)
    #3.
    p2.foreach(lambda (word, info_list): store(word, info_list))


'''
Function to store data to hbase.

The input should be a word and the list of (title, tfidf, pr)s to store.

Create a data dictionary:
        data = {
            'title': title,
            'word': word,
            'tfidf': tfidf,
            'pr': pr
        }

Use json.dumps(data) as the value to put into hbase.
'''
def store(word, info_list):
    connection = happybase.Connection(MACHINE)
    table = connection.table(INDEX_TABLE)
    b = table.batch()

    for title, tfidf, pr in info_list:
        data = {
            'title': title,
            'word': word,
            'tfidf': tfidf,
            'pr': pr
        }
        # Put data into hbase in the specified format
        b.put(word, {COLUMN_FAMILY + ':' + title: json.dumps(data)})
    b.send()


if __name__ == '__main__':
    spark = SparkContext(appName='hbase')
    hbase(spark)
    spark.stop()
