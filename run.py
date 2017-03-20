#!/usr/bin/python

import sys, getopt
import requests
import json
import os, fnmatch
import re
import shutil

# globals
article_file_indicator = '@article.*'
manual_file_indicator = '@toc.*'

# these are the handlebars you can use in an article file
article_handlebars = [
    "id",
    "title",
    "manual_id",
    "chapter_id",
    "last_edited_by",
    "last_edited_at",
    "meta_title",
    "meta_description",
    "meta_search",
    "created_at"]

# these are the handlebars you can use in manual file
# {{title}} outside of any blocks for manual title
# {{chapter}} to start and end the chapter, then {{title}} in the block
# {{article}} to start and end the manual, then {{title}} and {{link}} in the block

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

def find_file(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def remove_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)

def remove_found_files(files):
    for name in files:
        if os.path.exists(name):
            os.remove(name)

def write_file(directory, name, rawtext):
    with open(os.path.join(directory, name), 'w+') as f:
        f.write(rawtext.encode('utf-8'))

def copy_and_overwrite(from_path, to_path):
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)

def read_file(path):
    with open(path) as f:
        contents = f.read()
    return contents

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

    # if the output isn't specified, just put it in their home directory
    if (output_folder == ''):
        output_folder = os.path.expanduser('~')

    # if the template folder isn't specified, we'll just print out html files, otherwise we
    # have some prep work to do.
    if (template_folder == ''):
        template_specified = False
        is_manual_files = False
        print("Warn: Template folder not specified.  Will output HTML files only.")
    else:
        # check if template folder exists
        if os.path.exists(template_folder):
            template_specified = True

            # check if folder has an @article folder
            at_article_folder = os.path.join(template_folder, '@article')
            if os.path.exists(at_article_folder):
                print("Info: Template folder has @article folder.")

                # now let's see if there are @article file(s). we'll take as many
                # as you want, as long as there is at least one!
                at_article_file = find_file(article_file_indicator,at_article_folder)

                if at_article_file == []:
                    print("Error: No @article file found.")
                    sys.exit()

                # ok, phew we found at least one
                else:
                    print("Info: @article file(s) found.")

                    # read in template data
                    article_files = {}
                    for each_article_file in at_article_file:
                        article_files[each_article_file] = read_file(each_article_file)

            # no @article folder, that's a deal killer
            else:
                print("Error: Template folder did not have an @article folder.")
                sys.exit()

            # now let's check if theres a manual file
            at_manual_file = find_file(manual_file_indicator,template_folder)

            if at_manual_file == []:
                print("Warn: No @manual file found.")
                is_manual_files = False
            else:
                print("Info: @manual file(s) found.")
                is_manual_files = True

                # read in template data
                manual_files = {}
                manual_files_ref = {}
                for each_manual_file in at_manual_file:
                    manual_files[each_manual_file] = read_file(each_manual_file)

                    # Each @manual file consists of pre-chapter block, chapter block, and post-chapter block
                    # the chapter block then consists of the pre-article block, the article block, and post-article block
                    chapter_split = re.split('{{chapter}}',manual_files[each_manual_file])
                    article_split = re.split('{{article}}',chapter_split[1])
                    manual_files_ref[each_manual_file] = [
                                                chapter_split[0], # 0 - pre-chapter
                                                article_split[0], # 1 - pre-article (chapter)
                                                article_split[1], # 2 - article
                                                article_split[2], # 3 - post-article (chapter)
                                                chapter_split[2]] # 4 - post-chapter

        # template folder didn't exist
        else:
            print("Error: Template folder not found. Try 'run -h' if you need help.")
            sys.exit()

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

            # folder for site - two paths 1) template folder, 2) no template folder
            site_folder = os.path.join(output_folder, this_site_id)
            if template_specified:
                copy_and_overwrite(template_folder, site_folder)
            else:
                make_dir(site_folder)

            manuals = screensteps('sites/' + this_site_id) #grab manuals

            # loop through manuals
            for manual in manuals['site']['manuals']:
                this_manual_id = str(manual['id'])
                if (manual_id == this_manual_id) or (manual_id == ''): # only action a manual if manual isn't set, or is a match
                    print(">>> Processing manual: " + manual['title'])
                    print(">>> " + str(manual))

                    chapters = screensteps('sites/' + this_site_id + '/manuals/' + this_manual_id) # grab chapters

                    # pre-chapter replaces on str(manual_files_ref[path][0])
                    if is_manual_files: # are there templates?
                        manual_files_temp = {}
                        for path, details in manual_files.iteritems():
                            manual_files_temp[path] = []
                            manual_files_temp[path].append(str(manual_files_ref[path][0]).replace('{{title}}',chapters['manual']['title']))

                    # loop through chapters
                    for chapter in chapters['manual']['chapters']:
                        this_chapter_id = str(chapter['id'])
                        print(">>>> Processing chapter: " + chapter['title'])
                        print(">>>> " + str(chapter))

                        # pre-article replaces on str(manual_files_ref[path][1])
                        if is_manual_files: # are there templates?
                            for path, details in manual_files.iteritems():
                                manual_files_temp[path].append(str(manual_files_ref[path][1]).replace('{{title}}',str(chapter['title'])))

                        articles = screensteps('sites/' + this_site_id + '/chapters/' + this_chapter_id) # grab articles

                        # loop through articles
                        for article in articles['chapter']['articles']:
                            this_article_id = str(article['id'])
                            if (article_id == this_article_id) or (article_id == ''): # only action an article if article_id isn't set, or is a match
                                print(">>>>> Processing article: " + article['title'])
                                print(">>>>> " + str(article))

                                # folder for article - two paths 1) template folder, 2) no template folder
                                article_folder = os.path.join(site_folder, this_article_id)
                                if template_specified:
                                    copy_and_overwrite(at_article_folder, article_folder)
                                else:
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

                                if template_specified:
                                    # step through each file that starts with "@article"
                                    for path, temp_html in article_files.iteritems():
                                        temp_filename = this_article_id + os.path.splitext(path)[1]

                                        # find and replace {{html}}
                                        temp_towrite = temp_html.replace("""{{html}}""",article_html)

                                        # find and replace all the other handlebars specified
                                        for article_handlebar in article_handlebars:
                                            if article_handlebar != "link":
                                                temp_towrite = temp_towrite.replace(("{{" + str(article_handlebar) + "}}"),str(this_article['article'][article_handlebar]))

                                        # write file
                                        write_file(article_folder, temp_filename, temp_towrite)
                                else:
                                    # write html to a file if no templates
                                    write_file(article_folder, (this_article_id + '.html'), new_html)

                                # article replaces on str(manual_files_ref[path][2])
                                if is_manual_files: # are there templates?
                                    article_handlebars.append("link")

                                    for path, details in manual_files.iteritems():
                                        article_string = str(manual_files_ref[path][2])
                                        for article_handlebar in article_handlebars:
                                            if article_handlebar == "link":
                                                article_string = article_string.replace(("{{" + str(article_handlebar) + "}}"), this_article_id + '/' + this_article_id + os.path.splitext(path)[1] )
                                            else:
                                                article_string = article_string.replace(("{{" + str(article_handlebar) + "}}"),str(this_article['article'][article_handlebar]))
                                        manual_files_temp[path].append(article_string)

                        # post-article replaces on str(manual_files_ref[path][3])
                        if is_manual_files: # are there templates?
                            for path, details in manual_files.iteritems():
                                manual_files_temp[path].append(str(manual_files_ref[path][3]).replace('{{title}}',str(chapter['title'])))

                    # post-chapter replaces on str(manual_files_ref[path][4])
                    if is_manual_files: # are there templates?
                        for path, details in manual_files.iteritems():
                            manual_files_temp[path].append(str(manual_files_ref[path][4]).replace('{{title}}',chapters['manual']['title']))

                            # dump files
                            temp_filename = this_manual_id + os.path.splitext(path)[1]
                            write_file(site_folder, temp_filename, ''.join(manual_files_temp[path]))

        # clean up the "@" files that we copied over for each site
        if template_specified:
            site_article_folder = os.path.join(site_folder, '@article')
            try:
                remove_found_files(find_file(article_file_indicator,site_folder))
                remove_found_files(find_file(manual_file_indicator,site_folder))
                remove_directory(site_article_folder)
            except:
                print("We had trouble deleting the copied template files.  You can ignore any extra files.")


if __name__ == "__main__":
    main(sys.argv[1:])
