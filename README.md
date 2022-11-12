Use this tool to send you notification via Telegram when a sensor detects motion.

This bot is intended to be used on a Raspberry Pie with a motion sensor connected to it via GPIO.

## Installation

Install required tools:
```bash
$ sudo apt install python3 python3-pip
$ pip3 install build --upgrade
```

Install the package:

```bash
$ python3 -m build --sdist --wheel --outdir dist
$ pip3 install ./dist/*.whl
```

Start the bot:

```bash
$ uberwacher --help
```


