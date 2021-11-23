# python scaffold

This repository is a template for future projects that require a backend using python3.

### Configuration

See [`_settings.py`](src/archigetter/_settings.py).


## Development

[Install `poetry`](https://python-poetry.org/docs/#system-requirements) to work with this project.

Then:
1. Install all dependencies:
    ```sh
    > poetry install
    ```
2. Check whether `poe` was installed correctly
    ```sh
    > poetry run poe
    ```
3. Perform any additional setup required automatically:
    ```sh
    # This installs dependencies + performs additional setup, like registering pre-commit git hooks
    > poetry run poe install
    ```

From now on you should to use `poe` to cater to _all your needs_:
```sh
> poetry run poe

<...>

CONFIGURED TASKS
  style:check           Check the app code style
  style:fix             Check and autofix the app code style
  setup-precommit-hook  Setup the git pre-commit hock that checks for style errors
  install               Install all application dependencies
  test                  Run application tests
  dev                   Start the application in development mode (with hot reload)
  start                 Start the application in production mode
```

E.g., run `poetry run poe install` to install all dependencies or `poetry run poe test` to run application tests!

### Tooling

We use `poetry` for package management. Package managers have several advantages: Fixed and explicit versioning of dependencies, replication of same circumstances across different machines, ...

To manage development commands, we use [`poe` the poet](https://github.com/nat-n/poethepoet). This has several advantages. For development the main advantage is that there is no need to memorize the commands for all dev tools we use:
  - `poetry run poe style:fix` will fix the style for you,
  - `poetry run poe dev` will run dev mode of the application for you,
  - ...

For more `poe` goodness read [their feature overview](https://github.com/nat-n/poethepoet#features).

### FAQ

1. What formatting tools do we use?
    - we use [black](https://github.com/psf/black) for code-formatting
    - we use [isort](https://github.com/PyCQA/isort) for import formatting
    - both can resolve their own errors (for the most part)
    - **pro-tip:** Your code editor likely also supports using both with very little setup
        - VSCode: Open python file -> `CTRL/CMD + SHIFT + P` -> `Format Document` -> When asked select "Black" (instead of autopep8 or yapf or similar)
2. What tools do we use for testing?
    - flake8 to lint for common code errors and anti-patterns
    - mypy for typing
    - pytest for writing tests
