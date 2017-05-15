#!/usr/bin/python

import sys, getopt
import requests
import json
import os, fnmatch
import re
import shutil
import urlparse

# globals
article_file_indicator = '@article.*'
manual_file_indicator = '@toc.*'
image_folder_indicator = '@images'
attach_folder_indicator = '@attachments'
img_formats = [".tif", ".tiff", ".gif", ".jpeg", ".jpg", ".png"]

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
    local_filename = os.path.join(directory, short_path)
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

def find_dirs(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for dirname in dirs:
            if pattern in dirname.split():
                result.append(os.path.join(root, dirname))
    return result

def split_path(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

def remove_list_overlap(larger,smaller):
    for myitem in smaller:
        if myitem in larger:
            larger.remove(myitem)
    return larger

def find_relative_path(thispath,template_folder):
    relative_path = remove_list_overlap(split_path(thispath),split_path(template_folder))
    if len(relative_path[:-1]) > 0:
        relative_path = os.path.join(*relative_path[:-1])
    else:
        relative_path = ''
    return relative_path

def find_at_file_path(thispath,template_folder):
    relative_path = remove_list_overlap(split_path(thispath),split_path(template_folder))
    return os.path.join(*relative_path)

def remove_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)

def remove_directories(directories):
    for directory in directories:
        remove_directory(directory)

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
        is_article_folder = False
        is_manual_files = False
        is_image_folder = False
        is_attach_folder = False
        print("Warn: Template folder not specified.  Will output HTML files only.")
    else:
        # check if template folder exists
        if os.path.exists(template_folder):
            template_specified = True

            # check if folder has an @article folder
            at_article_folder = find_dirs("@article",template_folder)

            if len(at_article_folder) == 0:
                print("Info: No @article folder found.")
                is_article_folder = False
            elif len(at_article_folder) == 1:
                at_article_folder = at_article_folder[0]
                print("Info: Template folder has @article folder. "  + str(at_article_folder))
                is_article_folder = True
            else:
                print("Error: More than one @article folder found.")
                sys.exit()

            # check if folder has an @images folder
            at_images_folder = find_file(image_folder_indicator,template_folder)

            if len(at_images_folder) == 0:
                print("Info: No " + image_folder_indicator + " file found.")
                is_image_folder = False
            elif len(at_images_folder) == 1:
                at_images_folder = find_at_file_path(os.path.dirname(at_images_folder[0]),template_folder)
                print("Info: Template folder has " + at_images_folder[0] + " file. "  + str(at_images_folder))
                is_image_folder = True
            else:
                print("Error: More than one " + image_folder_indicator + " file found.")
                sys.exit()

            # check if folder has an @attachments folder
            at_attach_folder = find_file(attach_folder_indicator,template_folder)

            if len(at_attach_folder) == 0:
                print("Info: No " + attach_folder_indicator + " file found.")
                is_attach_folder = False
            elif len(at_attach_folder) == 1:
                at_attach_folder = find_at_file_path(os.path.dirname(at_attach_folder[0]),template_folder)
                print("Info: Template folder has " + at_attach_folder[0] + " file. "  + str(at_attach_folder))
                is_attach_folder = True
            else:
                print("Error: More than one " + attach_folder_indicator + " file found.")
                sys.exit()

            # now let's see if there are @article file(s). we'll take as many
            # as you want, as long as there is at least one!
            at_article_file = find_file(article_file_indicator,template_folder)

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

            # now let's check if theres a manual file
            at_manual_file = find_file(manual_file_indicator,template_folder)

            if at_manual_file == []:
                print("Warn: No @toc file found.")
                is_manual_files = False
            else:
                print("Info: @toc file(s) found.")
                is_manual_files = True

                # read in template data
                manual_files = {}
                manual_files_ref = {}
                for each_manual_file in at_manual_file:
                    manual_files[each_manual_file] = read_file(each_manual_file)

                    # Each @manual file consists of pre-chapter block, chapter block, and post-chapter block
                    # the chapter block then consists of the pre-article block, the article block, and post-article block
                    chapter_split = re.split('{{chapter}}',manual_files[each_manual_file])

                    if len(chapter_split) < 3:
                        chapter_split = ['',chapter_split[0],'']

                    article_split = re.split('{{article}}',chapter_split[1])

                    if len(article_split) < 3:
                        add_end_manual_file = article_split[0]
                        article_split = ['','','']
                    else:
                        add_end_manual_file = ''

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
    def screensteps_json(endpoint):
        base_url = 'https://' + site_name + '.screenstepslive.com/api/v2/'
        site_endpoint = base_url + endpoint
        try:
            r = requests.get(site_endpoint, auth=(user_id, api_token))
            if r.status_code == 200:
                return r.text
            else:
                print 'Error connecting to server (' + str(r.status_code) + ')'
                sys.exit(2)
        except requests.exceptions.RequestException:
            print 'Error connecting to server.'
            sys.exit(2)

    def screensteps(endpoint):
        rawtext = screensteps_json(endpoint)
        return json.loads(rawtext)

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
                    chapters_json = screensteps_json('sites/' + this_site_id + '/manuals/' + this_manual_id)

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

                                if is_article_folder:
                                    article_folder = os.path.join(site_folder, find_relative_path(at_article_folder,template_folder),this_article_id)
                                    copy_and_overwrite(at_article_folder, article_folder)
                                else:
                                    # write html to a file if no templates
                                    article_folder = site_folder

                                this_article_json = screensteps_json('sites/' + this_site_id + '/articles/' + this_article_id) # grab ind article
                                this_article = screensteps('sites/' + this_site_id + '/articles/' + this_article_id) # grab ind article

                                article_html = this_article['article']['html_body']

                                # loop through attached files
                                this_articles_files = []
                                for content_block in this_article['article']['content_blocks']:
                                    if content_block['url'] is not None:

                                        # what type of file is it?
                                        download_ext = os.path.splitext(urlparse.urlparse(content_block['url']).path)[1]
                                        if download_ext in img_formats: #image
                                            if is_image_folder:
                                                files_folder = os.path.join(site_folder,at_images_folder)
                                                short_files_folder = at_images_folder
                                                if '@article' in files_folder:
                                                    files_folder = files_folder.replace("@article",this_article_id)
                                                    short_files_folder = short_files_folder.replace("@article",this_article_id)
                                            else:
                                                files_folder = os.path.join(article_folder, 'images')
                                                short_files_folder = 'images'
                                                make_dir(files_folder)
                                        else: # attachment
                                            if is_attach_folder:
                                                files_folder = os.path.join(site_folder,at_attach_folder)
                                                short_files_folder = at_attach_folder
                                                if '@article' in files_folder:
                                                    files_folder = files_folder.replace("@article",this_article_id)
                                                    short_files_folder = short_files_folder.replace("@article",this_article_id)
                                            else:
                                                files_folder = os.path.join(article_folder, 'attachments')
                                                short_files_folder = 'attachments'
                                                make_dir(files_folder)

                                        print(">>>>>> Processing file: " + content_block['url'])
                                        new_file_path = download_file(files_folder,content_block['url'])
                                        this_articles_files.append([str(content_block['url']), os.path.join(short_files_folder,new_file_path)])

                                article_files_paths = []
                                if template_specified:
                                    # step through each file that starts with "@article"
                                    for path, temp_html in article_files.iteritems():

                                        back_dir = ''
                                        article_relative_path = find_relative_path(path,template_folder)
                                        temp_filename = this_article_id + os.path.splitext(path)[1]
                                        if article_relative_path != '':
                                            article_relative_path = article_relative_path.replace("@article",this_article_id)
                                            temp_filename = os.path.join(article_relative_path,temp_filename)
                                            back_dir = '../' * len(split_path(article_relative_path))

                                        # find and replace {{html}}
                                        temp_towrite = temp_html.replace("""{{html}}""",article_html)
                                        temp_towrite = temp_towrite.replace("""{{json}}""",(this_article_json).decode("unicode-escape"))

                                        # find and replace all the other handlebars specified
                                        for article_handlebar in article_handlebars:
                                            if article_handlebar != "link":
                                                temp_towrite = temp_towrite.replace(("{{" + str(article_handlebar) + "}}"),str(this_article['article'][article_handlebar]))

                                        for this_articles_file in this_articles_files:
                                            temp_towrite = temp_towrite.replace(this_articles_file[0],(back_dir + this_articles_file[1]))

                                        # write file
                                        write_file(site_folder, temp_filename, temp_towrite)
                                        article_files_paths.append(temp_filename)
                                else:
                                    for this_articles_file in this_articles_files:
                                        article_html = article_html.replace(this_articles_file[0],this_articles_file[1])
                                    write_file(article_folder, (this_article_id + '.html'), article_html)
                                    article_files_paths.append((this_article_id + '.html'))

                                # article replaces on str(manual_files_ref[path][2])
                                if is_manual_files: # are there templates?
                                    article_handlebars.append("link")

                                    for path, details in manual_files.iteritems():
                                        article_string = str(manual_files_ref[path][2])
                                        for article_handlebar in article_handlebars:
                                            if article_handlebar == "link":
                                                try:
                                                    same_ext_link = next(i for i in article_files_paths if os.path.splitext(i)[1] ==  os.path.splitext(path)[1])
                                                except:
                                                    print("Error: We didn't find a file extension match for the article from the TOC with: " + os.path.splitext(path)[1])
                                                    sys.exit()
                                                article_string = article_string.replace(("{{" + str(article_handlebar) + "}}"), same_ext_link)
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

                            manual_relative_path = find_relative_path(path,template_folder)
                            if manual_relative_path == '':
                                manual_relative_path = site_folder
                            else:
                                manual_relative_path = os.path.join(site_folder,manual_relative_path)

                            # dump files
                            temp_filename = this_manual_id + os.path.splitext(path)[1]
                            temp_file_contents = (''.join(manual_files_temp[path]) + add_end_manual_file)
                            temp_file_contents = temp_file_contents.replace("""{{json}}""",(chapters_json).decode("unicode-escape"))
                            write_file(manual_relative_path, temp_filename, temp_file_contents)

        # clean up the "@" files that we copied over for each site
        if template_specified:
            try:
                remove_found_files(find_file(article_file_indicator,site_folder))
                remove_found_files(find_file(manual_file_indicator,site_folder))
                remove_found_files(find_file(image_folder_indicator,site_folder))
                remove_found_files(find_file(attach_folder_indicator,site_folder))
                remove_directories(find_dirs("@article", site_folder))
            except:
                print("We had trouble deleting the copied template files.  You can ignore any extra files.")


if __name__ == "__main__":
    main(sys.argv[1:])