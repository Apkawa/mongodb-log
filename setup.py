
try:
    from setuptools import setup
except ImportError:
    from distutils import setup

setup(
      name='mongodb-log',
      version='0.1.1',
      description='Centralized logging made simple using mongodb',
      author='Andrei Savu',
      author_email='contact@andreisavu.ro',
      url='https://github.com/apkawa/mongodb-log/tree/master',
      packages=['mongolog'],
      install_requires=['pymongo']
)
