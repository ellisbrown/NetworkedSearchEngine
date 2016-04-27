from pyspark import SparkConf, SparkContext

import sys
import re

from variables import MACHINE, VUID, PAGE_TABLE, INDEX_TABLE, COLUMN_FAMILY, COLUMN

MIN_OCCURRENCES = 10
MAX_WORDS = 5000

index_file = 'hdfs:///user/%s/word_index' % VUID


'''
Complete the index function to write tuples: title,word, count
Where tuple and word are concatenated with title + ',' + word.

Write the output to <index_file> using saveAsTextFile(index_file)

Note that get_title_and_text returns a tuple (title, text).

You will need to write the is_frequent function to filter words that do not occur MIN_OCCURRENCES.

A good example can be found at: http://www.mccarroll.net/blog/pyspark2/
'''
def index(spark, wiki_file):
    wiki_data = spark.textFile(wiki_file)

    # do something
    wiki_data = wiki_data.map(lambda line: get_title_and_text(line)) \
        .flatMap(lambda (title, text): [(title + ',' + word, 1) for word in text]) \
        .reduceByKey(lambda x, y: x + y) \
        .filter(is_frequent) \
        .saveAsTextFile(index_file)

# return true if a word is frequent.
def is_frequent(index_record):
    return index_record[1] > MIN_OCCURRENCES


def get_title_and_text(text):
    return (get_title(text), get_text(text))


def get_title(text):
    title = '<title>'
    title_end = '</title>'
    start = text.index(title) + len(title)
    end = text.index(title_end)
    return text[start:end].lower()


def get_text(text):
    text_tag = '<text xml:space="preserve">'
    text_end = '</text>'
    start = text.index(text_tag) + len(text_tag)
    end = text.index(text_end)
    text_block = text[start:end].lower()
    return re.sub(r"\W+", ' ', text_block).strip().split(' ')[:MAX_WORDS]


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
    index(spark, sys.argv[2])
