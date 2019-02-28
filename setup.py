from setuptools import setup

setup(
        name='usb3.py',
        version='0.1',
        py_modules=['usb3.py'],
        python_requires='>3.0.0',
        install_requires=[
            
        ],
        entry_points='''
            [console_scripts]
            usb3.py=usb3.py:cli
        ''',
)
