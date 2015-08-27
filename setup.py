from setuptools import setup

setup(
    name="datagen",
    version="0.0",
    author="james absalon",
    author_email="james.absalon@rackspace.com",
    packages=['datagen'],
    package_data={'datagen': ['datagen/*']},
    long_description="""Simple tool for generating data into various backends."""
)
