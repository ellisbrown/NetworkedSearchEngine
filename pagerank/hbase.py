from pyspark import SparkConf, SparkContext

import happybase
import sys
import json

from variables import MACHINE, VUID, PAGE_TABLE, INDEX_TABLE, COLUMN_FAMILY, COLUMN

tf_idf_files = 'hdfs:///user/%s/tf_idf/*' % VUID
rank_files = 'hdfs:///user/%s/ranks/*' % VUID


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
    connection = happybase.Connection(MACHINE + '.vampire', table_prefix=VUID)
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
    conf = SparkConf()
    if sys.argv[1] == 'local':
        conf.setMaster("local[3]")
        print 'Running locally'
    elif sys.argv[1] == 'cluster':
        conf.setMaster("spark://10.0.22.241:7077")
        print 'Running on cluster'
    conf.set("spark.executor.memory", "10g")
    conf.set("spark.driver.memory", "10g")
    spark = SparkContext(conf = conf)
    hbase(spark)
