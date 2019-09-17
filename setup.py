from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='echelle',
      author=['G. Mirek Brandt, Curtis McCully, Timothy D. Brandt'],
      version='0.1.0',
      python_requires='>=3.5',
      packages=find_packages(),
      package_dir={'echelle': 'echelle'},
      setup_requires=['pytest-runner'],
      install_requires=requirements,
      tests_require=['pytest>=3.5'])
