# Contributing
Thanks for you interest in contributing to Budgetize.\
Contributing is simple and straightforward.\
You may choose on of the cards in the project's roadmap, fix an issue or add a feature you developed and if it passes all the reviews, it's going to merged.

# 💻 Preparing the Development Environment
## ⚙ Setting up dependencies

First you may clone the project with git.
```bash
git clone https://github.com/fer-hnndz/budgetize.git
cd budgetize
```

You'll then need to install all dependencies with `Pipenv` you may install the tool with pip before installing all dependencies with `pip install pipenv`.\
Once installed you may install budgetize's dependencies.
```bash
pipenv install Pipfile
pipenv shell
```
You'll then activate Pipenv's virtual environment that will allow you to run Budgetize with
``` bash
textual run main.py --dev
```
**NOTE: IT IS IMPORTANT YOU RUN THE APP WITH THIS COMMAND SINCE IF IT IS WITHOUT THE `--dev` FLAG OR RAN WITH THE PYTHON INTERPRETER, IT WILL CONNECT TO YOUR REAL BUDGETIZE DB INSTEAD OF THE TEST DATABASE.**\
You can also spawn a textual console that will allow you to see the app's output.\
In another terminal, spawn a pipenv shell and run:
```bash
textual console
```

## ✍ Git Workflow
I suggest you run `pre-commit install` so all checks are ran everytime you commit.\
For contributing, just follow these steps:
1. Create a branch for the feature you want to implement/bug to fix.
2. Be sure to comment anything useful for explanation and annotate functions the most you can.
3. Before committing, run `pre-commit run`.
4. Be sure to use present tense in commit messages. Example: **"Add/Solve feature x"** instead of **"Added/Solved feature x"**

When submitting your pull request make sure to name it accordingly and explain in detail what you changed. Thanks for contributing!
