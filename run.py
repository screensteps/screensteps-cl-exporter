#!/usr/bin/python

import sys, getopt
import requests
import json
import os
import re

# Define the help message here.
def print_help():
    print """
    Usage:
    run -n <site_name> -u <user_id> -p <token_password>
    [-t <template_folder>]
    [-o <output_folder>]
    [-s <site_id>]
    [-m <manual_id>]
    [-a <article_id>]

    Explanations:
    -n This is used for the name of the site (http://<site_name>.screenstepslive.com)
    -u Your user ID
    -p Your API token or password
    -t The folder with your templates (optional)
    -o The folder you would like with outputs (optional)
    -s If you'd like to only download one site, specify the ID here (optional)
    -m If you'd like to only download one manual, specify the ID here (optional)
    -a If you'd like to only download one article, specify the ID here (optional)

    Examples:
    run -n customerknowledge -u mikey -p mypassword -s 15226
    run -n myaccount -u johnsmith -p notAgoodPassword -a 21234
    """

def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_file(directory, url):
    short_path = url.split('/')[-1].split('?')[0]
    local_filename = directory + '/' + short_path
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return short_path

def write_file(directory, name, rawtext):
    with open(os.path.join(directory, name), 'w+') as f:
        f.write(rawtext.encode('utf-8'))

def main(argv):
    # Define variables we need.
    site_name = '' #n / site_name
    user_id = ''#u / user_id
    api_token = ''#p / password
    template_folder = '' #t / template
    output_folder = '' #o / output
    site_id = ''#s / site
    manual_id = ''#m / manual
    article_id = ''#a / article
    try:
        opts, args = getopt.getopt(argv,"hn:u:p:t:o:s:m:a:",["site_name=","user_id=","password=","template_folder=","output_folder=","site_id=","manual_id=","article_id="])
    except getopt.GetoptError:
        print 'use "run.py -h" for help'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-n", "--site_name"):
            site_name = arg
        elif opt in ("-u", "--user_id"):
            user_id = arg
        elif opt in ("-p", "--password"):
            api_token = arg
        elif opt in ("-t", "--template_folder"):
            template_folder = arg
        elif opt in ("-o", "--output_folder"):
            output_folder = arg
        elif opt in ("-s", "--site_id"):
            site_id = arg
        elif opt in ("-m", "--manual_id"):
            manual_id = arg
        elif opt in ("-a", "--article_id"):
            article_id = arg

    # check if required attributes exist
    if (site_name == '') or (user_id == '') or (api_token == ''):
        print("Site_name, user_id, and password are required. Try 'run -h' if you need help.")
        sys.exit()

    if (output_folder == ''):
        output_folder = os.path.expanduser('~')

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
            print 'Error connecting to server.'
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

            # folder for site
            site_folder = os.path.join(output_folder, this_site_id)
            make_dir(site_folder)

            manuals = screensteps('sites/' + this_site_id) #grab manuals

            # loop through manuals
            for manual in manuals['site']['manuals']:
                this_manual_id = str(manual['id'])
                if (manual_id == this_manual_id) or (manual_id == ''): # only action a manual if manual isn't set, or is a match
                    print(">>> Processing manual: " + manual['title'])
                    print(">>> " + str(manual))

                    # folder for manual
                    manual_folder = os.path.join(site_folder, this_manual_id)
                    make_dir(manual_folder)

                    chapters = screensteps('sites/' + this_site_id + '/manuals/' + this_manual_id) # grab chapters

                    # loop through chapters
                    for chapter in chapters['manual']['chapters']:
                        this_chapter_id = str(chapter['id'])
                        print(">>>> Processing chapter: " + chapter['title'])
                        print(">>>> " + str(chapter))

                        # folder for chapter
                        chapter_folder = os.path.join(manual_folder, this_chapter_id)
                        make_dir(chapter_folder)

                        articles = screensteps('sites/' + this_site_id + '/chapters/' + this_chapter_id) # grab articles

                        # loop through articles
                        for article in articles['chapter']['articles']:
                            this_article_id = str(article['id'])
                            if (article_id == this_article_id) or (article_id == ''): # only action an article if article_id isn't set, or is a match
                                print(">>>>> Processing article: " + article['title'])
                                print(">>>>> " + str(article))

                                # folder for article
                                article_folder = os.path.join(chapter_folder, this_article_id)
                                make_dir(article_folder)

                                this_article = screensteps('sites/' + this_site_id + '/articles/' + this_article_id) # grab ind article

                                article_html = this_article['article']['html_body']
                                new_html = article_html

                                for content_block in this_article['article']['content_blocks']:
                                    if content_block['url'] is not None:
                                        # folder for files
                                        files_folder = os.path.join(article_folder, 'files')
                                        make_dir(files_folder)

                                        print(">>>>>> Processing file: " + content_block['url'])
                                        new_file_path = download_file(files_folder,content_block['url'])
                                        new_html = new_html.replace(str(content_block['url']),('files/' + str(new_file_path)))

                                write_file(article_folder, 'raw.html', article_html)
                                write_file(article_folder, 'modified.html', new_html)


if __name__ == "__main__":
    main(sys.argv[1:])
