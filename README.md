![Deployement of book](../../actions/workflows/deploy-book.yml/badge.svg) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/cascadiaquakes/jupyter-book-template/HEAD?labpath=notebooks%2F)  
[Link to Jupyter-book template book](https://cascadiaquakes.github.io/jupyter-book-template/)

# jupyter-book-template

This repository is aimed to be a template/example to follow on how to make a jupyter-book for CRESCENT with the available resources such as logo

Requirements are:
- jupyter-book package  
- matplotlib  
- numpy
Then you will need the different packages for your own notebooks.

Compile: 
jupyter-book build mybookname/   (replace "mybookname" with the path to the folder containing the _config.yml file)

open the _build/html/index.html

More documentation on jupyter-book  
https://jupyterbook.org/en/stable/intro.html

# How to use this template

1. You should use this template to help you get started with jupyter-book. When creating a new repository, create it from template and select this one
2. Change this readme to reflect what your project actually is
3. In the readme, change the links of the build icon as well as the link to the deployed book
4. The _toc.yml is the table of content, this is where you define the structure of the book (sections, chapters etc...) More informations: https://jupyterbook.org/en/stable/structure/toc.html
5. The _config.yml should require minimal modifications: title, author. More information: https://jupyterbook.org/en/stable/customize/config.html
6. The notebook folder currently contains simple notebooks example, replace it by yours.
7. In the root folder, you have the intro.md and conclusion.md, modify this to fit your project
8. In the conclusion.md, there is an example on how to use reference and add the bibliography from the .bib file. more documentation: https://jupyterbook.org/en/stable/content/citations.html 
9. If you are using specific library and you want people to easily be able to run your notebooks, feel free to add packages to the requirement.txt. Currently the execution of the notebooks is blocked in the book, even at the compilation this is not needed to add all packages in it if the notebook are for demo purposes only and not meant to be used. Keep the requirements.txt in the root folder with at least jupyter-book for the automatic deployment.
