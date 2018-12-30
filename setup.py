import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

     name='armothy',  

     version='0.1',

     author="The Rusty Ducks",

     author_email="buisanguilhem@gmail.com",

     install_requires=[
          'smbus2',
      ],

     description="The library to control the 3 DoF robot arm for the 2019 French Robotics Cup.",

     long_description=long_description,

   long_description_content_type="text/markdown",

     url="https://github.com/therustyducks/armothy-python",

     packages=setuptools.find_packages(),

     classifiers=[

         "Programming Language :: Python :: 3",

         "License :: OSI Approved :: MIT License",

         "Operating System :: OS Independent",

     ],

 )
