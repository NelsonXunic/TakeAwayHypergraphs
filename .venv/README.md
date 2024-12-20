# *Take-Away on Hypergraphs*

## Description/Motivation

This project aims to develop a user-friendly application for playing the "Take Away" game on hypergraphs, explicitly focusing on nxm grids. The game involves two players taking turns removing vertices or hyperedges according to specific rules. The winner is the player who removes the last remaining piece. While the core gameplay is simple, analyzing winning strategies becomes increasingly complex as the grid size grows and, therefore, the need to build a program that can facilitate this. 
Ultimately, we want to:
- allow the users to practice the game to better understand the Take Away game on hypergraphs.
- collect gameplay data, particularly Nim values associated with different game states, which can be valuable for further research.
- make the game and its analysis more accessible than traditional research methods.

## Project Logo
![Project Logo](./logo.png)

## [Project Concept](./concept.md)

## Scope

This project aims to develop a core playable version of the "Playing Take Away on Hypergraphs" application. The initial focus will be on offering basic functionalities for playing the game on user-defined nxm grids. The application will include features like:
- Two-player turn-based gameplay.
- Visual representation of the game board (nxm grid).
- Functionality to remove vertices or hyperedges according to game rules.
- Ability to track the game state and determine the winner.
  
In terms of this project, we consider out of scope:
- Implementing an AI opponent (considered for future extensions).
- Advanced visualization tools for depicting winning strategies (potential future extension).
- Data analysis functionalities within the application (may be explored if time permits).
- Web-based version of the application (considered for future extensions).

## Vision

This project envisions an interactive and user-friendly application that facilitates learning and exploration of the Take Away game on hypergraphs. It aspires to bridge the gap between theoretical research and practical experience, allowing users to play, experiment, and gain a deeper understanding of the game mechanics. Additionally, the collected gameplay data can serve as a valuable resource for further research endeavors.

## Prerequisites

Ultimately, this application will be a desktop application (or a web app, depending on our chosen development environment). Users will need a computer with a standard operating system (Windows, Mac, or Linux) and an internet connection to download the application. The application will be developed using Python and Pygame, so users will need to have Python 3.x installed on their system. The application will also require the Pygame library to be installed.

[//]: # (## [Requirements]&#40;https://github.com/CSC493-Computing-Design-Practicum/csc493-cdp-NelsonXunic/blob/main/requirements.md&#41;)

[//]: # (## [Design]&#40;https://github.com/CSC493-Computing-Design-Practicum/csc493-cdp-NelsonXunic/blob/main/design.md&#41;)

[//]: # (## [Test Plan]&#40;test.plan.md&#41;)

## Built With
- **Python 3.x**: The primary programming language used for the project.
- **Pygame**: A library used for building the user interface and handling game mechanics.
- **PyCharm**: An IDE used for development, providing powerful tools for code editing, debugging, and testing.
- **Visual Studio Code**: Another IDE used for development, known for its versatility and extensive extensions.
- **sys**: Provides access to some variables used or maintained by the Python interpreter and to functions that interact strongly with the interpreter.
- **random**: Implements pseudo-random number generators for various distributions.
- **pickle**: Implements binary protocols for serializing and de-serializing a Python object structure.

## Author

- **Nelson Xunic**: *Playing Take-Away on Hypergraphs* [NelsonXunic](https://github.com/NelsonXunic)
- **About the Lead Developer:** Nelson D. Xunic Cua is a first-generation fourth-year student at Berea College where he is double majoring in Mathematics and Computer & Information Science. He was born and raised in the mountainside of Guatemala and coming from a low-income family, he wants to support students from Guatemala who are interested in studying science but do not have the resources to do so. 
In his free time, he enjoys learning origami while listening to music. He is also passionate about all kinds of crafts, his favorite being broomcraft. His favorite form of exercise is running, he says it helps him focus on his academics as he uses it as away to distress. He joined the cross-country and track teams during his third year at Berea College. He prefers long-distance events over sprints and short-distance events.

## Acknowledgments

- The author would like to thank the following individuals and organizations for their support and contributions to this project: 
  - Dr. Barnard, for introducing the concept of Take Away games on hypergraphs. Inspiration is drawn from Dr. Barnard's Doctoral Dissertation, ["Some Take-Away Games on Discrete Structures"](https://uknowledge.uky.edu/math_etds/44/)(2017)
  - The Undergraduate Research and Creative Projects Program at Berea College for allowing me to work on this research with Dr. Barnard during the Summer 2024.
  - Prof. Wilborne and the Computer Science Department at Berea College for providing the opportunity to work on this project as part of the Computing Design Practicum course.
  - My classmates for their support and feedback throughout the project.
  - My family and friends for their encouragement and motivation.
  
## [Setup and Use Guide](./setup.md)

## License
This project is licensed under the [MIT](./LICENSE) License.