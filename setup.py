from setuptools import setup, find_packages

setup(
    name="zebraPy",
    description='Standalone script to communicate with Zebra Printers over USB',
    version="0.4dev",
    author="Lucas Hopkins",
    packages=['zebraPy'],
    scripts=['bin/usb_0.4.py'],
    install_requires=[
        'socket',
        'tkinter',
        'binascii',
        'logging',
        'os',
        'subprocess',
        'sys',
        'time',
        'datetime',
        'pyusb',
        'pyfiglet'
    ],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },
)