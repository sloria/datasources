# -*- coding: utf-8 -*-

import os
import re
import time
import httplib
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

SUBREDDITS = ['programming', 'python', 'django', 'flask']
HEADER = ['subreddit', 'users', 'date']
MODULE = os.path.dirname(os.path.abspath(__file__))


def parent_dir(path):
    '''Return the parent of a directory.'''
    return os.path.abspath(os.path.join(path, os.pardir))

REPO_DIR = os.environ.get("OPENSHIFT_REPO_DIR", parent_dir(MODULE))
# Where to save the data
DATA_FILE = os.path.join(REPO_DIR, 'wsgi', 'data', 'python-subreddit-traffic.csv')
DELAY = 10

BASE = 'http://reddit.com'
NON_DECIMAL_REGEX = re.compile(r'[^\d.]+')
HTTP_HEADER = {'User-Agent': 'Python subreddit user counter'}


def main():
    # Check if the header exists
    header_line = ','.join(HEADER) + '\n'
    with open(DATA_FILE, 'a+') as fp:
        fp.seek(0)
        first_line = fp.readline()
        if first_line != header_line:
            write_header(DATA_FILE, header_line)

    # Get the user counts for each subreddit
    connection = httplib.HTTPConnection("www.reddit.com")
    for i, subreddit in enumerate(SUBREDDITS):
        count = get_user_count(connection, subreddit)
        central = pytz.timezone('US/Central')
        local_time = central.localize(datetime.now())
        row = '{subreddit},{count},{time}'.format(subreddit=subreddit,
                count=count, time=local_time.strftime('%Y-%m-%d %H:%M:%S'))
        # Write the data to csv
        with open(DATA_FILE, 'a+') as fp:
            fp.write(row + '\n')
        print(row)
        if i != len(SUBREDDITS) - 1:
            time.sleep(DELAY)


def write_header(filename, header):
    '''Writes a header line to a file.'''
    with open(filename, 'r') as original:
        data = original.read()
    with open(filename, 'w') as newfile:
        newfile.write(header + data)
    return None


def get_user_count(connection, subreddit):
    '''Scrape the user count for a subreddit.'''
    url = '/r/' + subreddit
    connection.request('GET', url, headers=HTTP_HEADER)
    html = connection.getresponse().read()
    soup = BeautifulSoup(html)
    user_count_str = soup.select('p.users-online span.number')[0].text
    return int(strip_nonnumeric(user_count_str))


def strip_nonnumeric(s):
    return NON_DECIMAL_REGEX.sub('', s)


if __name__ == '__main__':
    main()
