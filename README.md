# ScreenSteps Command Line Exporter

This is the source code for the ScreenSteps command line exporter. It is written in Python and supports Python 2.

## Usage

```
ss_exporter -n <account_name> -u <user_id> -p <token_password>
[-t <template_folder>]
[-o <output_folder>]
[-s <site_id>]
[-m <manual_id>]
[-a <article_id>]
[-M <manual_file_name>]
[-i object_identifier]
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
-M By default a manual file uses the manual id for the filename. This parameter allows you to specify a specific name for the manual file. Requires that -m be passed in as well.
-i Specifies how the site, manual, and article files should be named. By default the "id" from ScreenSteps is used. You can set this to "title" or "title_id". "name_id" will use the name with " [ID]" appended to the end.
```

## Examples:

```
# Export a manual using a template from a folder name "my_template" folder.
# Store the output in a folder named "output".
ss_exporter -n customerknowledge -u jack -p mypassword -t my_template_folder -o output_folder -s 15226 -m 53243

# Export a single article
ss_exporter -n myaccount -u jill -p apassword -t my_template_folder -o output_folder -s 15226 -a 21234

# Export a single article and name the file using the article title
ss_exporter -n myaccount -u jill -p apassword -t my_template_folder -o output_folder -s 15226 -a 21234 -i title
```

## Template structure

You can tell the exporter how to format the output by passing in the path to a template folder using the `-t` option. The exporter looks for certain files within the template folder to determine the structure of the output.

- `@toc.html` or `@toc.json`: This file will be replaced with the manual table of contents. The `@toc` portion of the file name will be replaced with the numerical id of the manual on the ScreenSteps server. The file suffix determines if HTML or JSON content will be inserted into the file.
- `@article.html` or `@article.json` file: The folder where either of these files resides determines where articles will be placed. The `@article` portion of the file name will be replaced with the numerical id of the article on the ScreenSteps server. The file suffix determines if HTML or JSON content will be inserted into the file.
- `@images`: Files used in articles will be placed in the directory where this file is located. If the `@images` file is in a folder named `@article` then a different folder will be created for each article. The folder will be named using the naming format specified by the `-i` parameter and the images for the article will be placed inside.
- `@attachments`: Behaves the same as the `@images` file but specifies where attachments will be stored. This can be in the same directory as the `@images` folder.

Look in the `samples` directory for working examples.

### Example template:

- :open_file_folder: my_template_folder
  - :open_file_folder: articles
    - @article.html
  - :open_file_folder: images
    - :open_file_folder: @article
      - @images
      - @attachments
  - @toc.html

## Example template output:

```
ss_exporter -n myaccount -u jack -p apassword -t my_template_folder -o output_folder -s 15226 -a 21234
```

- :open_file_folder: output_folder
  - :open_file_folder: articles
    - 122472.html
    - 122473.html
    - 122474.html
    - 122475.html
  - :open_file_folder: images
    - :open_file_folder: 122472
      - image_1.png
      - image_2.png
    - :open_file_folder: 122473
      - image_1.png
      - image_2.png
    - :open_file_folder: 122474
      - image_1.png
      - image_2.png
    - :open_file_folder: 122475
      - image_1.png
      - image_2.png
  - 21234.html

## Installation

To build from python (".py") file into single file executable, follow these steps:

1. Ensure the python file runs on your system (and all dependencies are installed), with something like this:
    `python ss_exporter.py -n SCREENSTEPS_ACCOUNT_NAME -u USERNAME -p PASSWORD -t my_template_folder -o output_folder -s SITE_ID -a ARTICLE_ID`
    You may need to install the `requests` module. For information on installing modules please visit https://packaging.python.org/tutorials/installing-packages/
2. Remove any previous build & dist folders
    `rm -rf build dist`
3. Build
    `pyinstaller --onefile ss_exporter.py`

## Support

Email support@screensteps.com with any questions or bug reports.
