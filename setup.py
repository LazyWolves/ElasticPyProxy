# setup.py
from setuptools import setup
import setuptools


def readme():
    return "EP2"
    #with open('README.rst') as f:
        #return f.read()

def get_dependencies():
  with open("requirements.txt") as req:
    lines = req.readlines()
    lines = [line.strip() for line in lines]
    return lines

setup(name='elasticpyproxy-1.0-djmgit',
      version='0.1',
      description='A controller for haproxy for autoscaling backends.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 1.0',
        'License :: GPL',
        'Programming Language :: Python :: 3.6',
        'Topic :: Automation :: Systems :: Devops',
      ],
      keywords='haproxy automation cloud devops systems',
      url='https://github.com/djmgit/ElasticPyProxy',
      author='Deepjyoti Mondal',
      author_email='djmdeveloper060796@gmail.com',
      license='GPL',
      packages=setuptools.find_packages(),
      install_requires=get_dependencies(),
      entry_points={
          'console_scripts': ['ep2=src.driver.driver:drive'],
      },
      include_package_data=True,
      zip_safe=False)