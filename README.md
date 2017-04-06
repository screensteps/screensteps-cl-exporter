## Synopsis

This is the ScreenStepsLive API exporter that builds into a template.

## Usage

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

## Installation

To build from python (".py") file into single file executable, follow these steps:
  1. Ensure the python file runs on your system (and all dependencies are installed), with something like
      python run.py -n customerknowledge -u mikey -p mypassword -s 15226
  2. Remove any previous build & dist folders
      rm -rf build dist
  3. Build
      pyinstaller --onefile run.py

Contact mike@smblytics.com for further help.

## License

Belongs to Trevor DeVore.
