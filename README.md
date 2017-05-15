# ScreenSteps Command Line Exporter

This is the source code for the ScreenSteps command line exporter. It is written in Python.

## Usage

```
run -n <account_name> -u <user_id> -p <token_password>
[-t <template_folder>]
[-o <output_folder>]
[-s <site_id>]
[-m <manual_id>]
[-a <article_id>]
```

## Explanations:

```
-n This is used for the name of your ScreenSteps account (http://<site_name>.screenstepslive.com)
-u Your user ID
-p Your API token or password
-t The folder with your templates (optional)
-o The folder you would like with outputs (optional)
-s If you'd like to only download one site, specify the ID here (optional)
-m If you'd like to only download one manual, specify the ID here (optional)
-a If you'd like to only download one article, specify the ID here (optional)
```

## Examples:

```
# Export a manual using a template from a folder name "my_template" folder.
# Store the output in a folder named "output".
run -n customerknowledge -u jack -p mypassword -t my_template_folder -o output_folder -s 15226 -m 53243

# Export a single article
run -n myaccount -u jill -p apassword -t my_template_folder -o output_folder -s 15226 -a 21234
```

## Template structure

You can tell the exporter how to format the output by passing in the path to a template folder using the `-t` option.

- :open_file_folder: articles
  - @article.html
- :open_file_folder: images
  - :open_file_folder: @article
    - @images
- @toc.html

## Installation

To build from python (".py") file into single file executable, follow these steps:

1. Ensure the python file runs on your system (and all dependencies are installed), with something like this:
    `python run.py -n SCREENSTEPS_ACCOUNT_NAME -u USERNAME -p PASSWORD -t my_template_folder -o output_folder -s SITE_ID -a ARTICLE_ID`
2. Remove any previous build & dist folders
    `rm -rf build dist`
3. Build
    `pyinstaller --onefile run.py`

## Support

Email support@screensteps.com with any questions.
