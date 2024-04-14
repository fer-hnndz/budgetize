# Contributing
Thanks for you interest in contributing to Budgetize.\
Contributing is simple and straightforward.\
You may choose on of the cards in the project's roadmap, fix an issue or add a feature you developed and if it passes all the reviews, it's going to merged.

**Table of Contents**\
1. [💻 Preparing the Development Environment](#💻-preparing-the-development-environment)
    - [⚙ Setting up dependencies](#⚙-setting-up-dependencies)
    - [✍ Git Workflow](#✍-git-workflow)
2. [🌎 Translating](#🌎-translating)

# 💻 Preparing the Development Environment
## ⚙ Setting up dependencies

First you may clone the project with git.
```bash
git clone https://github.com/fer-hnndz/budgetize.git
cd budgetize
```

You'll then need to install all dependencies with `poetry`. You may install the tool with pip before installing Budgetize's dependencies. You may refer to this guide [here](https://python-poetry.org/docs/#installation)
Once installed you may install budgetize's dependencies.
```bash
poetry install Pipfile
poetry shell
```
You'll then activate poetry's virtual environment that will allow you to run Budgetize with
``` bash
textual run main.py --dev
```
**NOTE: IT IS IMPORTANT YOU RUN THE APP WITH THIS COMMAND SINCE IF IT IS WITHOUT THE `--dev` FLAG OR RAN WITH THE PYTHON INTERPRETER, IT WILL CONNECT TO YOUR REAL BUDGETIZE DB INSTEAD OF THE TEST DATABASE.**\
You can also spawn a textual console that will allow you to see the app's output.\
In another terminal, spawn a poetry shell and run:
```bash
textual console
```

## ✍ Git Workflow
It is suggested you run `poetry run pre-commit install` so all checks are ran automatically everytime you commit.\
For contributing, just follow these steps:
1. Create a branch for the feature you want to implement/bug to fix.
2. Be sure to comment anything useful for explanation and annotate functions the most you can.
3. Before committing, run `poetryrun pre-commit run`. (You may skip this if you already installed pre-commit)

When submitting your pull request make sure to name it accordingly and explain in detail what you changed. Thanks for contributing!

# 🌎 Translating
**NOTE: This section needs to be improved. And commands checked**
Create a folder with the locale you want to translate.

Commands:
If you need to extract new translations to the template file:

```bash
poetry run pybabel extract ./budgetize -o ./budgetize/translations/TRANSLATION_TEMPLATE.po --project Budgetize
```

To create a new translation
Create a folder called with your locane and add a folder called `LC_MESSAGES`

```bash
poetry run pybabel init -D budgetize -i ./budgetize/translations/TRANSLATION_TEMPLATE.po -o ./budgetize/translations/{locale}/{locale}.po -l {locale}
```

Compilation:
```bash
poetry run pybabel compile -D budgetize -l {locale} -i {your_translation}.po -d ./budgetize/translations/{locale}
```

Updating Translations:
```bash
poetry run pybabel update -i .\budgetize\translations\TRANSLATION_TEMPLATE.po -o .\budgetize\translations\{locale}\{locale}.po -l {locale} --previous --update-header-comment -D budgetize
```

Compile Translations
```bash
poetry run pybabel compile -D budgetize -l {locale} -i {your_translation}.po -d ./budgetize/translations/
```
