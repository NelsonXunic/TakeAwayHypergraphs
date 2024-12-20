# Playing Take-Away on Hypergraphs

## Goals
- Develop a user-friendly application for playing the Take-Away game on nxm hypergrids.
- Collect and store gameplay data, particularly Nim values, to contribute to further research on Take Away games on hypergraphs.

## Context
The Take Away game is a classic combinatorial game where players take turns removing objects from a pile, and the winner is whoever removes the last piece. This proposal focuses on a variation played on hypergraphs, specifically nxm grids. On their turn, each player can choose to do one of the following:
- remove a vertex and all of the hyperedges that contain it
- remove a hyperedge with all of the hyperedges that contain it.

While the rules seem simple, analyzing winning strategies for this game becomes increasingly complex with larger grids since one must explore all possible game states to determine a winning strategy. Each game state is categorized using a non-negative integer assigned to it that we refer to as [Nim value](https://mathworld.wolfram.com/Nim-Value.html#:~:text=To%20find%20the%20nim%2Dvalue,string%20as%20a%20decimal%20number.). Existing research primarily focuses on theoretical analysis and heuristic approaches. While valuable, these methods can be challenging for those new to the game or 
wanting to visualize strategies. Also, due to the nature of the game, one may get repeated game states while analyzing different gameplays or within the same gameplay.

## Novelty
This project offers an opportunity to study Take Away games on hypergraphs by creating an interactive application. Users can play and experiment with the game, making it more accessible and intuitive. Hopefully, more people will get interested in it and choose to contribute to the project. Additionally, the data collection feature provides valuable resources for further research. Ideally, the initial game state will be chosen randomly to help analyze possible winning strategies.

## Functionality
- Implement a user interface for playing Take Away on nxm grids.
- Allow users to select the grid size.
- Designate a turn-based playing system for two players (optional: AI opponent).
- Provide a visual representation of the game state.
- Integrate functionality to track and store Nim values associated with each game state.
- Offer options for exporting collected data for analysis.
- Give an option to users to play on a randomly generated grid.

## Audience
This application targets several audiences:
- Mathematics and Computer Science students: Explore the game mechanics and visualize winning strategies.
- Game enthusiasts: Enjoy a unique variation of the Take Away game.
- Researchers: Utilize collected data to further analyze winning strategies for Take Away on hypergraphs.

## Challenges
- Implementing an efficient algorithm for calculating and storing Nim values for various grid sizes.
- Designing an intuitive and user-friendly interface for playing the game.
- Ensuring data security and privacy for collected gameplay information.

## Measures
The project will be considered successful if it achieves the following:
- Functional and user-friendly application for playing Take Away on hypergraphs.
- Ability to collect and export Nim values for various game states.
- Positive user feedback regarding the application's usability and educational value.

## Motivation
My primary motivation is to create a tool that bridges the gap between theoretical research and practical exploration of Take Away games on hypergraphs. This project will allow individuals to learn and experiment with the game in an interactive setting, potentially fostering greater interest in combinatorial game theory and mathematical research in general. Additionally, the collected data can contribute to future research efforts.

## Future Extensions
- Implement an AI opponent with varying difficulty levels.
- Integrate advanced visualization tools to depict winning strategies for different grid sizes.
- Develop a web-based version of the application for wider accessibility.

## Other
This project aligns with my interest in developing educational tools using programming skills. It provides an opportunity to explore game theory concepts and contribute to research in a practical way.