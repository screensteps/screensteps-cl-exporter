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

You can tell the exporter how to format the output by passing in the path to a template folder using the `-t` option. The exporter looks for certain files within the template folder to determine the structure of the output.

- `@toc.html` or `@toc.json`: This file will be replaced with the manual table of contents. The `@toc` portion of the file name will be replaced with the numerical id of the manual on the ScreenSteps server. The file suffix determines if HTML or JSON content will be inserted into the file.
- `@article.html` or `@article.json` file: The folder where either of these files resides determines where articles will be placed. The `@article` portion of the file name will be replaced with the numerical id of the article on the ScreenSteps server. The file suffix determines if HTML or JSON content will be inserted into the file.
- `@images`: Files used in articles will be placed in the directory where this file is located. If the `@images` file is in a folder named `@article` then a different folder will be created for each article. The folder will be named using the numerical id of the article on the ScreenSteps server and the images for the article will be placed inside.

Look in the `samples` directory for a working example.

### Example template:

- :open_file_folder: my_template_folder
  - :open_file_folder: articles
    - @article.html
  - :open_file_folder: images
    - :open_file_folder: @article
      - @images
  - @toc.html

## Example template output:

```
run -n myaccount -u jack -p apassword -t my_template_folder -o output_folder -s 15226 -a 21234
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
    `python run.py -n SCREENSTEPS_ACCOUNT_NAME -u USERNAME -p PASSWORD -t my_template_folder -o output_folder -s SITE_ID -a ARTICLE_ID`
2. Remove any previous build & dist folders
    `rm -rf build dist`
3. Build
    `pyinstaller --onefile run.py`

## Support

Email support@screensteps.com with any questions or bug reports.
