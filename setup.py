from setuptools import setup, find_packages

setup(
    name='movie_review_stars',
    version='0.1',
    description='Automated way for movie critic to rank movies',
    author='Lucas Moura',
    author_email='lucas.moura128@gmail.com',
    packages=find_packages(),
    test_suite="tests",
    )
