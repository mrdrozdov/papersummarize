papersummarize
==============

Getting Started
---------------

- Change directory into your newly created project.

    cd papersummarize

- Create a Python virtual environment.

    python3 -m venv env

- Upgrade packaging tools.

    env/bin/pip install --upgrade pip setuptools

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Configure the database.

    env/bin/initialize_papersummarize_db development.ini

- Run your project's tests.

    env/bin/pytest

- Run your project.

    env/bin/pserve development.ini


FAQ
---

- Q: Where did this code find inspiration?

    https://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/wiki/authorization.html

- Q: Where did this idea find inspiration?

    https://github.com/zakird/revsub

- Q: Where is the theme from?

    https://www.deviantart.com/
