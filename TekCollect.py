#!/usr/bin/python


# This is tekCollect! This tool will scrape specified data types out of a URL or file.
# @TekDefense
# Ian Ahl | www.TekDefense.com | 1aN0rmus@tekDefense.com
# *Some of the Regular Expressions were taken from http://gskinner.com/RegExr/
# Version: 1.0

# Changelog:

# Import libraries
import re
import argparse
import urllib2
import sqlite3
import datetime
import ConfigParser

# Adding arguments
parser = argparse.ArgumentParser(description='tekCollect is a tool that will scrape a file or website for specified data')
parser.add_argument('-u', '--url', help='This option is used to search for hashes on a website')
parser.add_argument('-f', '--file', help='This option is used to import a file that contains hashes')
parser.add_argument('-d', '--database', help='This option is used to specify a database name to search or create')
parser.add_argument('-o', '--output', help='This option will output the results to a file.')
parser.add_argument('-r', '--regex', help='This option allows the user to set a custom regex value. Must encase in single or double quotes.')
parser.add_argument('-t', '--type', help='This option allows a user to choose the type of data they want to pull out. Currently supports ')
parser.add_argument('-s', '--summary', action='store_true', default=False, help='This options will show a summary of the data types in a file')
args = parser.parse_args()

# Initialize lists and variables
listResults = []
listSum = []
today = datetime.datetime.now()
now = today.strftime("%Y-%m-%d")

ini = 'config.ini'
sect = 'Regex'
config = ConfigParser.RawConfigParser()
config.read(ini)
regTypes = dict(config.items(sect))
listTypes = []
for regType in regTypes:
    regVal = config.get(sect, regType)
    listTypes.append((regType, regVal))

if args.url:
    target = args.url
    stripHTTP = re.sub('(http|https)://', '', target)
    dbName = now + '_' + stripHTTP + '.db'

if args.file:
    target = args.file
    stripSlash = re.sub('/','_', target)
    dbName = now + '_' + stripSlash + '.db'

if args.database:
    dbName = args.database

if args.type:
    for t in listTypes:
        if args.type.upper() == t[0].upper():
            rVal = t[1]
            rtype = t[0]

def createDB():
    con = sqlite3.connect(dbName)
    with con:
        cur = con.cursor()
        con.text_factory = str
        cur.execute('CREATE TABLE IF NOT EXISTS COLLECTION(DATE TEXT, TARGET TEXT, TYPE TEXT, FOUND TEXT, UNIQUE (DATE, TARGET, TYPE, FOUND))')
        con.commit()


def regexContent(content):
    global listResults
    global listSum
    global rVal
    global rtype
    if args.summary is True:
        for val in listTypes:
            regVal = val[1]
            regType = val[0]
            regexValue = re.compile(regVal)
            regexSearch = re.findall(regexValue, content)
            for res in regexSearch:
                res = ''.join(res)
                con = sqlite3.connect(dbName)
                with con:
                    cur = con.cursor()
                    con.text_factory = str
                    cur.execute("INSERT OR IGNORE INTO COLLECTION(DATE, TARGET, TYPE, Found) VALUES(?,?,?,?)", (now, target, regType, res))
                    con.commit()

    else:
        regexValue = re.compile(rVal)
        regexSearch = re.findall(regexValue, content)
        for res in regexSearch:
            res = ''.join(res)
            con = sqlite3.connect(dbName)
            with con:
                cur = con.cursor()
                con.text_factory = str
                cur.execute("INSERT OR IGNORE INTO COLLECTION(DATE, TARGET, TYPE, Found) VALUES(?,?,?,?)", (now, target, rtype, res))
                con.commit()


def webscrape(tgtURL):
    proxy = urllib2.ProxyHandler()
    opener = urllib2.build_opener(proxy)
    try:
        response = opener.open(target)
        content = response.read()
        contentString = str(content)
        regexContent(contentString)
    except Exception, e:
        print str(e)


def filescrape(iFile):
    fileImport = open(target)
    try:
        for i in fileImport:
            regexContent(i)
    except Exception, e:
        print str(e)


def resultsprint():
    global rtype
    con = sqlite3.connect(dbName)
    con.text_factory = str
    with con:
        if args.summary is False:
            cur = con.cursor()
            cur.execute("Select * From COLLECTION WHERE TYPE=?", [rtype])
            rows = cur.fetchall()
            for row in rows:
                print '[+] Found: ' + row[3]
        else:
            cur = con.cursor()
            cur.execute("Select TYPE, COUNT(TYPE) From COLLECTION Group BY TYPE")
            rows = cur.fetchall()
            for row in rows:
                print '[+] ' + row[0] + ': ' + str(row[1])

createDB()

if args.file:
    filescrape(target)
elif args.url:
    webscrape(target)

resultsprint()
