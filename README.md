# Networked Search Engine
> *This is an open-ended final project for [Dr. Janos Sallai](mailto:janos.sallai@vanderbilt.edu)'s Networks course at Vanderbilt University.*

We created a networked search engine with an Android App interface that queries an indexed copy of Wikipedia stored in HBase.

We adapted a project from [Dr. Dan Fabbri](mailto:daniel.fabbri@vanderbilt.edu)'s BigData course in which we implemented a simple version of pagerank to rank search results of keywords on a *small subset* of Wikipedia. For this project, we set up a cluster on AWS to run the Spark jobs that compile indexes of the *full* Wikipedia directory to HBase tables stored on our cluster. We also created an EC2 cloud server on which we host a python server that receives search requests via python's socket package. The server queries our HBase table and returns a list of up to 10 page titles and links from Wikipedia sorted by pagerank. Our Android client app connects to the EC2 server and sends a user generated list of search queries to the server. Upon receiving the response from the server, the app displays the list of page titles as links to the page on Wikipedia.


## Example

##### Client:
~~~
>>> nc localhost 20000
Search for terms on wikipedia
.............................
>>> air jordan
"Air Jordan,https://en.wikipedia.org/wiki/Air_Jordan|Air Melo Line,https://en.wikipedia.org/wiki/Air_Melo_Line|Jumpman (logo),https://en.wikipedia.org/wiki/Jumpman_(logo)|Air Arabia Jordan,https://en.wikipedia.org/wiki/Air_Arabia_Jordan|Michael Jordan,https://en.wikipedia.org/wiki/Michael_Jordan|Tinker Hatfield,https://en.wikipedia.org/wiki/Tinker_Hatfield|Just Jordan,https://en.wikipedia.org/wiki/Just_Jordan|Second Generation (advertisement),https://en.wikipedia.org/wiki/Second_Generation_(advertisement)|Mars Blackmon,https://en.wikipedia.org/wiki/Mars_Blackmon|23 (song),https://en.wikipedia.org/wiki/23_(song)"
>>>
>>> Q
~~~

##### Server:
~~~
>>> python server.py
Connected by ('::1', 52977, 0, 0)
Client is searching for "air jordan"
Sending results to client
.
Terminating connection
>>>
~~~


## Installation

See the README in pagerank/ for instructions on setting up and running the Spark jobs to create the HBase tables used in the search functionality.

## Authors

Ellis Brown
: <ellis.l.brown@vanderbilt.edu> --  [@ellisbrown](https://github.com/ellisbrown)

Danny Carr
: <daniel.p.carr@vanderbilt.edu> --  [@dcarr45](https://github.com/dcarr45)


*[Networks course]:  CS 4283
*[HBase]: Apache HBase
*[AWS]: Amazon Web Services
*[EC2]:Amazon Elastic Compute Cloud
*[BigData course]: CS 3892
