import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    # own
    'markdown',
    'PyGments',
    'pyramid-jinja2',
    ]

setup(name='myblog',
      version='0.0',
      description='myblog',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Reimund Klain',
      author_email='webmaster@daymien.de',
      url='daymien.de',
      keywords='web wsgi bfg pylons pyramid blog',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='myblog',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = myblog:main
      [console_scripts]
      populate_myblog = myblog.scripts.populate:main
      """,
      )

