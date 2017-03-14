#!/usr/bin/python

import sys, getopt
import requests
import json

def main(argv):
    # Define variables we need.
    site_name = 'customerknowledge' #n / name
    user_id = 'mkarp' #u / user
    api_token = 'silly' #p / password
    template_folder = '' #t / template
    output_folder = '' #o / output
    site_id = '15226' #s / site
    manual_id = '58254' #m / manual
    article_id = '612809' #a / article
    try:
        opts, args = getopt.getopt(argv,"hn:u:p:t:o:s:m:a:",["name=","user=","password=","template_folder=","output_folder=","site_id=","manual_id=","article_id="])
    except getopt.GetoptError:
        print 'run.py -i <inputfile> -o <outputfile>'
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

    # set up request
    def screensteps(endpoint):
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

    # grab all sites for that user information
    print("> Pulling sites")
    sites = screensteps('sites') # grab sites
    print("> " + str(sites))

    # loop through sites
    for site in sites['sites']:
        this_site_id = str(site['id'])
        if (site_id == this_site_id) or (site_id == ''): # only action a site if site_id isn't set, or is a match
            print(">> Processing site: " + site['title'])
            print(">> " + str(site))
            manuals = screensteps('sites/' + this_site_id) #grab manuals

            # loop through manuals
            for manual in manuals['site']['manuals']:
                this_manual_id = str(manual['id'])
                if (manual_id == this_manual_id) or (manual_id == ''): # only action a manual if manual isn't set, or is a match
                    print(">>> Processing manual: " + manual['title'])
                    print(">>> " + str(manual))

                    chapters = screensteps('sites/' + this_site_id + '/manuals/' + this_manual_id) # grab chapters

                    # loop through chapters
                    for chapter in chapters['manual']['chapters']:
                        this_chapter_id = str(chapter['id'])
                        print(">>>> Processing chapter: " + chapter['title'])
                        print(">>>> " + str(chapter))

                        articles = screensteps('sites/' + this_site_id + '/chapters/' + this_chapter_id) # grab articles

                        # loop through articles
                        for article in articles['chapter']['articles']:
                            this_article_id = str(article['id'])
                            if (article_id == this_article_id) or (article_id == ''): # only action an article if article_id isn't set, or is a match
                                print(">>>>> Processing article: " + article['title'])
                                print(">>>>> " + str(article))

                                this_article = screensteps('sites/' + this_site_id + '/articles/' + this_article_id) # grab ind article
                                print("-- BEGIN HTML --")
                                print(this_article['article']['html_body'])
                                print("-- END HTML --")


if __name__ == "__main__":
    main(sys.argv[1:])
