from setuptools import setup

setup(name='pebbles_smoke_test',
      version='0.1.0',
      packages=['.'],
      description="Simple UI smoke tester for Pebbles instances",
      entry_points={
          'console_scripts': [
              'pebbles-smoke-test = pebbles_smoke_test:main'
          ]
      },
      install_requires=["selenium"]
      )
