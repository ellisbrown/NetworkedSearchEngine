# PageRank Readme

## Instructions

### Setup
Run the setup.py script to create your Hbase environment.

    python setup.py

#### Delete
If you want to delete the table and start over, run:

    python setup.py delete

If you want to scan the data in a table run (print 100 rows):

    python setup.py scan

### Index words
Initially run on a small file locally. This will save the output to hdfs in your directory.

    pyspark spark_index.py local hdfs:///tmp/wiki/wiki_page_per_line_small.txt

To see the output, run:

    hadoop fs -cat /path/word_index/*


#### Delete
If you want to re-run the code, you need to delete or move the output directory. To delete, run:

    hadoop fs -rm -f -R /path/word_index

To run on the subset of wikipedia that has 'ball' on the cluster run:

    pyspark spark_index.py cluster hdfs:///tmp/wiki/wiki_page_per_line_ball.txt

### Extract Links
Initially run on a small file locally. This will save the output to hdfs in your directory.

    links.py local hdfs:///tmp/wiki/wiki_page_per_line_small.txt

You should see the following output:

    hadoop fs -cat /path/link_index/*

#### Delete
You can delete the output with:

    hadoop fs -rm -f -R /path/link_index

To run on the subset of wikipedia that has 'ball' on the cluster run:

    pyspark links.py cluster hdfs:///tmp/wiki/wiki_page_per_line_ball.txt

### Calculate Term Frequency - Inverse Document Frequency

  Identify important words in a page.

    pyspark tfidf.py cluster

  You can view the output with:

    hadoop fs -cat /path/tf_idf/* | less

  Sample output looks like:

      (u'michael jordan', u'the', 0.11754849790361308)
      (u'michael jordan', u'mvp', 8.459374812297817)
      (u'michael jordan', u'jordan', 26.485210266492054)

#### Delete
  You can delete the output with:

      hadoop fs -rm -R -f /path/tf_idf

### Page Rank

  Use the extracted links to calculate page rank.

      pyspark page_rank.py cluster 10

  The 10 refers to the number of iterations to run.

  To view the results run:

      hadoop fs -cat /path/ranks/* | less

  The highest ranked pages at the end of the file (if sorted) will look like:

      (u'baseball', 94.58879758629737)
      (u'football (soccer)', 99.82634799064857)
      (u'basketball', 104.69536483500916)
      (u'college football', 106.4944323069795)
      (u'national football league', 120.6350040323033)
      (u'major league baseball', 127.80469819047917)
      (u'american football', 177.01236495305528)
      (u'united states', 204.68917317253945)
      (u'wikipedia:persondata', 291.7456160982039)
      (u'category:living people', 312.91471412995185)
      (u'association football', 358.5487286834513)

#### Delete
  You can delete the results with:

      hadoop fs -rm -r -R /path/tf_idf

### Happy Base

  Store the results of the tf-idf and page rank computation in Hbase. You will store:

      word -> {'column_family:page_title': {'title': title, 'word': word, 'tfidf': tfidf, 'pr': pr}}

  To do a small test, try:

      pyspark hbase.py local

  To run across the cluster, run:

      pyspark hbase.py cluster

  You can check your results by running:

      python setup.py scan

### Search

  Given a keyword search (which may contain multiple words), return the top-K (10) pages.
  You should use the scoring function: tf-idf + W * page\_rank.
  Rank pages by that scoring function.

  To search for pages with 'nfl' do:

      python search.py nfl

  The results I see with W = 4 are:

      Searching for ['nfl']
      [(708.8916152258975, u'american football'), (485.6541559373692, u'national football league'), (426.36064572769106,
      u'college football'), (133.80996584050172, u'quarterback'), (97.05174604543102, u'super bowl'), (87.51840899591404,
      u'green bay packers'), (76.15414544127205, u'american football league'), (70.42001501075907, u'new york giants'),
      (69.00211121715267, u'chicago bears'), (63.60110284177957, u'washington redskins')]

  TO search for pages with 'air jordan' do:

      python 6_search.py air jordan

  The results I see are:

      Searching for ['air', 'jordan']
      [(68.45531560644798, u'air jordan'), (26.296558543734292, u'tinker hatfield'), (13.631317260002795, u'fibber mcgee and molly')]
