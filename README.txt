pyramid-wiki
============

Getting Started
---------------

- Change directory into your newly created project.

    cd pyramid_wiki

- Create a Python virtual environment.

    python3 -m venv env

- Upgrade packaging tools.

    env/bin/pip install --upgrade pip setuptools

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Configure the database.

    env/bin/initialize_pyramid_wiki_db development.ini

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
