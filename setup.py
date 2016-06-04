from distutils.core import setup
import challonge


setup(name="pychallonge",
      author="Fabien Poupineau",
      url="http://github.com/fp12/pychallonge",
      version=challonge.__version__,
      packages=[
          'challonge',
      ],
      install_requires=[
          'iso8601>=0.1.11'
      ]
      )
