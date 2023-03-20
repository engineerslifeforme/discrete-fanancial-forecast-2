from setuptools import setup, find_packages

setup(
    name='financial_planner',
    version='1.0.0',
    url='',
    author='Author Name',
    author_email='author@gmail.com',
    description='Description of my package',
    packages=find_packages(),    
    install_requires=['pyyaml', 'beautiful-date', 'pandas'],
)