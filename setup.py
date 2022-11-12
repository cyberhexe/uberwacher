#!/usr/bin/env python3

version = "1.0.0"

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='uberwacher',  # Required
    version=version,  # Required
    description="Telegram bot that notifies if there's a movement caught by a connected motion sensor",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/totekuh/uberwacher',  # Optional
    author='totekuh',  # Optional
    author_email='totekuh@protonmail.com',  # Optional
    classifiers=[  # Optional
        'Development Status :: 5 - Production/Stable',

        'Environment :: Console',

        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',

        'License :: OSI Approved :: MIT License',

        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='motionsensor, sensor, motion, gpio, flask',  # Optional
    package_dir={'': './src'},  # Optional
    packages=find_packages(where='src'),  # Required
    python_requires='>=3.6, <4',
    install_requires=[
        "python-telegram-bot",
        "gpio"
    ],  # Optional
    entry_points={  # Optional
        'console_scripts': [
            'uberwacher=uberwacher.telegram_uberwacher:main',
        ],
    },

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/totekuh/uberwacher/issues',
        'Source': 'https://github.com/totekuh/uberwacher',
    },
)
