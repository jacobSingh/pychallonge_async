from distutils.core import setup
import challonge


setup(name="pychallonge_async",
      author="Fabien Poupineau (fp12)",
      url="http://github.com/fp12/pychallonge_async",
      version=challonge.__version__,
      keywords = ['tournaments', 'challonge'],
      packages=[
          'challonge',
      ],
      install_requires=[
          'iso8601>=0.1.11',
          'aiohttp'
      ]
      )
