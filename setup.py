from setuptools import setup

try:
    long_description = open('README.md').read()
except IOError:
    long_description = ''

setup(name='popo-fsm',
      version='0.0.1',
      description='Plain old python object finite state machine support.',
      long_description=long_description,
      url='https://github.com/redpandalabs/popo-fsm',
      py_modules=['popo_fsm'],
      license='MIT License',
      author='Red Panda Innovation Labs',
      author_email='nitish@redpanda.co.in',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
      ])
