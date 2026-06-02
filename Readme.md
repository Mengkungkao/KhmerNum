Note: 
If your python version is higher than 3.13, you need to install 3.13 for pygame, cuz the 3.14 having problem with building wheels

after install python3.13

use this to check the different version of python u have:
py -0p

then cd to enter this /KhmerNum 

create venv for python 3.13
py -3.13 -m venv .venv

update setup tools:
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel

to install pygame:

.venv\Scripts\python.exe -m pip install pygame --only-binary=:all:

save it:
.venv\Scripts\python.exe -m pip freeze > requirements.txt

commit to github:
git add requirements.txt .gitignore
git commit -m "Add pygame dependency"
git push
