# PySweeper
PySweeper is an application for automatically solving the Windows (7) Minesweeper game using OpenCV template matching for extracting the board state and a Python Win32 wrapper for moving / clicking the mouse.
Creator: P H, ph1387@t-online.de 

---

## Overview
This application can solve the different game field sizes quite reliably. But at some times guessing a safe spot is necessary and can not be avoided due to the nature of the game. After using OpenCV template matching for the first time I would say that directly reading the Process' memory or using another form of image regognition would have been easier and far less error prone since the size of the game must match the templates. Scaling either the image or the templates is an option but causes massive matching errors.
The needed Python-Modules are located in the requirements.txt inside the project.

<p align="center">
  <img width="600" height="370" src="https://github.com/p1387h/PySweeper/blob/master/play_large.gif">
</p>

## Instructions

### How to run

The instructions are written for a usage on a Windows machine. If you're using Linux or IOS, then these might differ slightly.
Navigate into the project folder where the requirements.txt is located:
```sh
cd PySweeper\MinesweeperPlayer
```

**Optional but recommended if not used skip to the end of the optional block**

install virtualenv, create a virtual environment for the project called "pySweeper" and activate it.

```sh
python -m pip install --user virtualenv
python -m virtualenv pySweeper
pySweeper\Scripts\activate
```

A successful activation shows the folder name in front of the command line. I.e.:

``` sh
(pySweeper) C:\Users\X\Desktop\PySweeper\MinesweeperPlayer
```

**End of the optional block**

Install all requirements for the project using pip:

```sh
pip install -r .\requirements.txt
```

Now start the Minesweeper game. Make sure to use the default (smallest) size since this project relies on image recognition.
Run the project with the following command. After that two windows will open and the console waits until a button is pressed.

```sh
python Main.py
```

**Not needed if no environment was created**

Deactivate the environment with the following command. You can enable it again later if needed.

```sh
pySweeper\Scripts\deactivate.bat
```

### How it works

#### Idea
The general idea of the application can be split in four steps:

- Get an image of the game
- Extract the relevant information from the image
- Find the next position(s) to click
- Use the Win32 API to click at the position(s)

The releavant information are the changes after each click since each click on an unchecked square results in a change of the board state.
The main components of the application are the following classes:

|Class|Function|
|-|-|
|Game|Container for all game information|
|Window|Provides the window image as well as the clicking functionality|
|OpenCV|Extracts the image information using template matching|
|DecisionMaker|Decides the positions that are going to be clicked next|
|SquareWrapper|Wrapper for the Square class. Generates the scores used in the DecisionMaker|

#### Decision making
The application uses a score system for deciding which square is going to be clicked next. Each one of them gets assigned a value matching their number in the game. If this values exactly matches the number of unchecked squares around a target one, these unchecked squares decrease the value of each square around them. This must be done since these ones are definitely bombs. Once a squares value is decreased to zero, all other neighbours, that are not considered bombs, are recognized as safe and can be clicked one after another.

<p align="center">
  <img width="511" height="321" src="https://github.com/p1387h/PySweeper/blob/master/decision_making.png">
</p>

## License
MIT [license](https://github.com/p1387h/PySweeper/blob/master/LICENSE.txt)
