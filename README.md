# Pebbles Smoke Test

This repository contains a simple smoketest runner for [pebbles](https://github.com/CSCfi/pebbles).

It is intended to be run by `cron` on a separate small VM or Docker container
and to publish a simple string that can be served via e.g. Nginx and consumed
by external monitoring tools via a HTTP API.

Intended installation is

    pip install  git+https://github.com/CSCFi/pebbles-smoke-test.git@master

No need to clutter PyPI with yet another package that nobody uses.

The intended call is something like

    python pebbles-smoke-test -c config.json > /var/www/status.txt

For an example of config.json see example_config.json. Supported drivers are
PhantomJS for headless running and Firefox for desktop/debugging.

In case of errors the driver attempts to store a dated screenshot at
configurable `img_path`.

## Requirements

Phantom.js and GeckoDriver if Firefox is required.

## Configuration

For command line parameters run

    pebbles-smoke-test --help

For config.json parameters read example_config.json or read the source code.

## Known issues

System may not log out correctly on PhantomJS due to localstorage not being
purged. Should investigate if this becomes a recurrent issue.
