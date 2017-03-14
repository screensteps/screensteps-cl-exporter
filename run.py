#!/usr/bin/python

import sys, getopt
import requests
import json

def main(argv):
    # Define variables we need.
    site_name = 'customerknowledge'
    user_id = 'mkarp' #u / user
    api_token = 'silly' #p / password
    template_folder = '' #t / template
    output_folder = '' #o / output
    site_id = '14885' #s / site
    manual_id = '61817' #m / manual
    article_id = '' #a / article
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile> -o <outputfile>'
            sys.exit()
        #elif opt in ("-i", "--ifile"):
            #inputfile = arg
        #elif opt in ("-o", "--ofile"):
            #outputfile = arg
    #print 'Input file is "', inputfile
    #print 'Output file is "', outputfile

    # set up URLs
    def ss_request(endpoint):
        base_url = 'https://' + site_name + '.screenstepslive.com/api/v2/'
        site_endpoint = base_url + endpoint
        try:
            r = requests.get(site_endpoint, auth=(user_id, api_token))
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                print 'Error connecting to server (' + str(r.status_code) + ')'
                sys.exit(2)
        except requests.exceptions.RequestException:
            print 'Error connecting to server (' + str(r.status_code) + ')'
            sys.exit(2)

    print("Connected to Sites")
    t = ss_request('sites')
    print(t)

if __name__ == "__main__":
    main(sys.argv[1:])
