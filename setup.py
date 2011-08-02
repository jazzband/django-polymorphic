from distutils.core import setup

setup(
    name = 'django_polymorphic',
    version = '0.2',
    description = 'Seamless Polymorphic Inheritance for Django Models',
    author = 'Bert Constantin',
    author_email = 'bert.constantin@gmx.de',
    maintainer = 'Christopher Glass',
    maintainer_email = 'tribaal@gmail.com',
    packages = [ 'polymorphic' ],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
