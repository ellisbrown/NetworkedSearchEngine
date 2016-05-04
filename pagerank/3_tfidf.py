from pyspark import SparkConf, SparkContext

from variables import MACHINE, BUCKET, PAGE_TABLE, INDEX_TABLE, COLUMN_FAMILY, COLUMN

import sys

index_file = BUCKET + 'word_index/*'
tf_idf_file = BUCKET + 'tf_idf'


'''
Term frequency inverse document frequency
https://en.wikipedia.org/wiki/Tf%E2%80%93idf

Input:
(u'akrotiri and dhekelia,are', 22)
(u'john roddam spencer stanhope,by', 20)
(u'outline of japan,div', 21)


term frequency(t, d) = # of times t occurs in d / number of words in d
inverse document frequency(t, D) = # of distinct pages in the corpus / # of pages t occurs in D

1. Count the number of words in d. Output should be: (title, count)
2. Determine the frequency of t in a page. Output should be: (title, word, term-freq)
3. Count the number of distinct pages: Output should be a single int
4. Determine the inverse document frequency. Output should be: (word, inverse-doc-freq)
5. Calculate tf-idf. Output should be: (title, word, tf-idf)
6. Save output to tf_idf_file

You will need to use the keyBy function to join.

You will want to use groupBy and reduceByKey.

Save the result to the <tf_idf_file> (i.e., saveAsTextFile(tf_idf_file)).

It is also useful to use sortBy on title and tf-idf to look at the final results.

'''
def tf_idf(spark):
    word_data = spark.textFile(index_file)
    lines = word_data.map(lambda line: eval(line)) \
        .map(lambda line: split_input(line))

    titles = lines.keyBy(lambda (title, word, count): title)

    # 1. number of words in a document
    d_count = lines.map(lambda (title, word, count): (title, count)) \
        .reduceByKey(lambda x, y: x + y)

    #2 frequency of t in a page
    t_freq = titles.join(d_count.keyBy(lambda (title,count): title)) \
        .map(lambda (title, ((t1, w, c), (t2,d))): (t1, w, 1.0 * c/d)) \

    #.saveAsTextFile(tf_idf_file)

    #3 number distinct pages
    num_pages = lines.map(lambda (title, word, count): title).distinct().count()

    #4 inverse document frequency
    idf = lines.map(lambda (title, word, count): (word, 1)) \
        .reduceByKey(lambda x, y: x + y) \
        .map(lambda (word, count): (word, 1.0 * num_pages / count)) \

    #5 tf-idf, #6 save output to file
    tf_idf = t_freq.keyBy(lambda (title, word, tf): word) \
        .join(idf.keyBy(lambda (word,idf): word)) \
        .map(lambda (word, ((title, w1, tf), (w2, idf))): (title, word, tf * idf)) \
        .sortBy(lambda (title, word, tfidf): (title, tfidf)) \
        .saveAsTextFile(tf_idf_file)


'''
Take line from input file and convert to tuple of (title, word, count)
'''
def split_input(line):
    return line[0].split(',')[0], line[0].split(',')[1], line[1]



if __name__ == '__main__':
    spark = SparkContext(appName='tfidf')
    tf_idf(spark)
    spark.stop()
