Bitso Organizations ETL
============

Simple ETL app, that extract records from Bitso's `order_book` api and write them to partitioned files. The files are primarily 
partitioned by book and then by extraction date. The first one to make it easier to navigate into a single book and the second one 
to make it simpler to find new data, it's not necessary to use source system's timestamp.
Also, I decided to use `year`, `month` and `day` explicitly, easier to navigate through S3. 
For API docs: [Bitso API docs](https://docs.bitso.com/bitso-api/docs/list-open-orders)
 
Build & Run
------------
Build: The application is dockerized, so you will need [Docker](https://www.docker.com/get-started/) to wrap it up.
~~~bash
    $ docker build . --tag=bitso
~~~

Run:
There's a docker compose set up for running the application for both books BTC_MXN and USD_MXN
~~~bash
    $ docker compose up 
~~~
This will start extracting files to `book=btc_mxn` and `book=usd_mxn` folders.

Run the commands below to stop:
~~~bash
    $ docker compose stop 
    $ docker compose rm
~~~

If you want to run it for one specific book, use the command below:
The `--book` parameter must be provided. 
~~~bash
    $ docker run --name bitso -d --volume $(pwd)/book=<book>:/home/bitso/book=<book> bitso --book=<book>
~~~

Tests:
If you want to run the tests, run those in the root directory. Five tests must be collected.
~~~bash
    $ pip install -r requirements.txt
    $ coverage run -m pytest
    $ coverage report -m 
~~~

About the Project
------------
```
.
├── Dockerfile
├── README.md
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
├── src
│   ├── __init__.py
│   └── bitso_etl.py
└── tests
    ├── __init__.py
    ├── conftest.py
    └── test_bitso_etl.py
```
Here in this project I'm writing to local to simplify the process, if some other destination is required, the `load()` method must be adjusted.

How to Automate?
------------
If the idea is to have a containerized environment, the app is ready.
I can think of two ways of automating it, one it's treating it as a daemon and keep it running all the time dumping files.
It's possible to add health checks and monitor it using Datadog for example. 
Another possibility is having Airflow triggering small batches.

Known issues
------------
1. I used MacOS (M1) to build this project, I had issues in the past running MacOS projects on Linux, let me know if you have any issues and I can try to adjust.
2. Some parameters are hard coded to make the app easier to evaluate, that must be adjusted for production environment. 
3. I'm using the sandbox api that doesn't require authentication, I was not able to register myself in Bitso. 
4. I would like to get extra points by using Webhooks, but I didn't get exactly how to use them in this case. Have another app receiving the records and dumping them maybe?
5. I adjusted the dump to run every 60 records, it's easier to see the files being written.


Final Thoughts
------------
Definitely there is room for improvement in the project, I would be glad to jump into a call, so we can discuss that together.
Thank you for the opportunity! 
