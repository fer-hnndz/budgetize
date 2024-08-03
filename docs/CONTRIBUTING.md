# Contributing
Thanks for you interest in contributing to Budgetize.\
Contributing is simple and straightforward.\
You may choose on of the cards in the project's roadmap, fix an issue or add a feature you developed and if it passes all the reviews, it's going to merged.

**Table of Contents**
- [💻 Preparing the Development Environment](#💻-preparing-the-development-environment)
    - [⚙ Setting up dependencies](#-setting-up-dependencies)
    - [✍ Git Workflow](#-git-workflow)
- [🌎 Localizing](#🌎-localizing)
    - [Extracting Translatable Strings](#extracting-translatable-strings)
    - [The Localizing Workflow](#-the-localizing-workflow)
        - [Creating a New Locale File](#creating-a-new-locale-file)
        - [Updating Locale Files](#updating-locale-files)
    - [Localizing Strings](#localizing-strings)
    - [Compiling Locales](#compiling-locales)

# 💻 Preparing the Development Environment
## ⚙ Setting up dependencies

First you may clone the project with git.
```bash
git clone https://github.com/fer-hnndz/budgetize.git
cd budgetize
```

You'll then need to install all dependencies with `poetry`. You may install the tool with pip before installing Budgetize's dependencies. You may refer to this guide [here](https://python-poetry.org/docs/#installation).\
Once installed you may install Budgetize's dependencies.

```bash
poetry install
```
To run Budgetize from source use the command in the root of the project folder:
```
poetry run textual run main.py --dev
```
**NOTE: IT IS IMPORTANT YOU RUN IN DEV MODE WITH THE `--dev` FLAG. OTHERWISE IT WILL CONNECT TO YOUR REAL BUDGETIZE DB INSTEAD OF THE TEST DATABASE.**\
You can also spawn a textual console that will allow you to see the app's output.\
In another terminal, run:
```bash
poetry run textual console
```

## ✍ Git Workflow
It is suggested you run `poetry run pre-commit install` so all checks are ran automatically everytime you commit.\
For contributing, just follow these steps:
1. Create a branch for the feature you want to implement/bug to fix.
   - Use `feature/feature-name` if you are going to implement a feature
   - Use `bugfix/bug-name` if you are solving a bug. 
2. Be sure to comment anything useful for explanation and annotate functions the most you can following the [Google Docstring Style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).
3. Before committing, run `poetry run pre-commit run`. (You may skip this if you already installed pre-commit)

When submitting your pull request make sure to name it accordingly and explain in detail what you changed. Thanks for contributing!

# 🌎 Localizing
This section will guide you through the process of localizing (translating) messages within Budgetize.

## Extracting Translatable Strings
All translatable strings (*aka. those strings wrapped with `_()`*) are those strings that a user will see in the UI. These strings need to be extracted to a `*.po` file and translated for Babel to use them accordingly.\
To extract translatable strings run:

```bash
pybabel extract ./budgetize -o ./budgetize/translations/TRANSLATION_TEMPLATE.po --project Budgetize
```

This will serve as the template for all other Locale files and their respective translations.\
**NOTE: THE TEMPLATE SHOULD ONLY BE UPDATED IF NEW TRANSLATABLE STRINGS WERE ADDED**

# 💬 The Localizing Workflow
This section details the process of creating/updating locale files.\
Please follow carefully since you don't want to mess existing translations.

## Updating the Translatable Strings
### Creating a New Locale File
*Please refer to [Updating Locale Files](#updating-locale-files) if the locale file already exists.*\
**DO NOT RUN ANY OF THIS COMMANDS FOR EXISTING LOCALES. OTHERWISE PREVIOUS TRANSLATIONS WILL BE OVERWRITTEN.**


To create a new locale, head over to `budgetize/translations` and create a folder.
1. Create a folder and name it with your locale (Ex. `en` for English)
2. Create a folder called `LC_MESSAGES` in your newly created folder.
3. Once you've created those folders, run this command to generate the file to write the translations:
```bash
pybabel init -D budgetize -i ./budgetize/translations/TRANSLATION_TEMPLATE.po -o ./budgetize/translations/{locale}/{locale}.po -l {locale}

# Example
poetry run pybabel init -D bugetize -i ./budgetize/translations/TRANSLATION_TEMPLATE.po -o ./budgetize/translations/es/es.po -l es
```

### Updating Locale Files
Every once in a while more translatable strings may be added to the translations template. To extract these new strings, you may run the command:

```bash
pybabel update -i .\budgetize\translations\TRANSLATION_TEMPLATE.po -o .\budgetize\translations\{locale}\{locale}.po -l {locale} --previous --update-header-comment -D budgetize

# Example
pybabel update -i .\budgetize\translations\TRANSLATION_TEMPLATE.po -o .\budgetize\translations\es\es.po -l es --previous --update-header-comment -D budgetize
```

## Localizing Strings
Now, for every generated `msgid` line, which is the translatable string, write below the `msgstr` which is the string translated to the specified locale.\
**EXAMPLE IN SPANISH (locale `es`)**
```
# budgetize\...\...
msgid "Income"
msgstr "Ingresos"

# budgetize\...\...
msgid "Food"
msgstr "Alimentos"

# budgetize\...\...
msgid "Groceries"
msgstr "Supermercado"

# budgetize\...\...
msgid "Medicine"
msgstr "Medicina"
```

If you ever want to know the context of the string, above `msgid` is the location on the codebase where the string was extracted. This can help understanding the context.

#### Fuzzy Translations
You may want to use your text editor and search for `fuzzy` translations.\
These are translations that Babel attempted to automatically translate, but may need to be checked by a human to confirm if it is correct.\
**Once you checked it, delete the line containing the `fuzzy`**


## Compiling Locales
Once you have translated the strings into a new locale, you may compile those strings in a `.mo` file for Babel to detect the locale.\
To compile your locale run:
```bash
pybabel compile -D budgetize -l {locale} -i budgetize/translations/{locale}/{locale}.po -d ./budgetize/translations/{locale}

# Example
pybabel compile -D budgetize -l es -i budgetize/translations/es/es.po -d ./budgetize/translations/es
```
