from setuptools import setup

setup(
    name='aworker',
    version='0.1',
    packages=['aworker', 'aworker.queue', 'aworker.tests'],
    url='https://github.com/skruger/aworker',
    license='MIT',
    author='Shaun Kruger',
    author_email='shaun.kruger@gmail.com',
    description='Task queue worker that can process functions written in regular python and asyncio coroutines.'
)
