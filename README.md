# Wave Function Collapse Project

<img width="1463" height="885" alt="Screenshot 2026-05-05 100956" src="https://github.com/user-attachments/assets/a796475e-eb44-4d25-9fcc-457268ecaa1d" />

## Overview

As part of our formal languages and finite automata course, we implemented the Wave Function Collapse (WFC) algorithm to generate worlds given a sample of a world to generate. In this project, both two-dimensional and three-dimensional WFC implemented, though we focused on the latter.


## Algorithm Basics
The first part of the algorithm is analyzing an inputted world sample. For our implementation, this means processing a png like:

<img width="263" height="267" alt="image" src="https://github.com/user-attachments/assets/36ed65db-5baa-4564-bac4-294966a1ebc0" />

Next, the user specifies a tile size that they want to work with. The sample is then scanned for every unique tile present in it. Additionally, we collect every rotation of each tile to have more robust tiling later on. For the example above, all of the 2x2 tiles with rotations are as follows:

<img width="393" height="258" alt="image" src="https://github.com/user-attachments/assets/1d31f022-dce4-43d0-ad84-34fd429220f7" />

Now, with all the tiles collected, we look at how the different tiles can connect to one another. In our implementation, if a tile is compared to another such that the first tile's north side matches with second's south, then the second tile is allowed to be placed north of the first. We realize this using an adjacency matrix for each direction, which for a if an entry $m_{i,j} = 1$ then tile j can be placed in a given direction from tile i. 

At this point, we begin to think of these tiles as states and the adjacency matrices encoding rules about how these states can exist next to each other. To generate a sample, we create a grid of the desired size containing what states can be allowed where. At the start of the algorithm, since nothing has been decided, any grid point can be in any state. A WFC step is then as follows: we pick the state with the least amount of options, choose a random state that the tile could possibly be in, and then propagate the change. For example, if we decide to turn a tile into a water tile, and have that water can only be placed next to other water or sand, then the tiles around the water tile cannot have grass in them. This in turn causes the neighbors of the original tile to change, and those changes have to be propagated aswell. The WFC step is over once all changes have been propagated. The world is then done generating once all of the tiles have been decided on. Below is an example of a world generated of the previous example, but with a 3x3 tile size.

<img width="498" height="504" alt="image" src="https://github.com/user-attachments/assets/15671864-419a-4e34-84b9-0ff2dcca3f2b" />

Sometimes, we can place tiles in a manner such that another tile has no legal options, which means at some point we made a mistake when choosing a tile. To solve this issue, our WFC implementation includes a backtracking solver, where we backtrack tile placements until we no longer reach illegal states. Some WFC implementations instead opt to throw away the current generation and just restart, however illegal states become considerably more common as the complexity of the sample increases. Since we planned on developing 3D generation, the backtracking was a must. Here are some more examples of worlds generated with our 2D algorithm:

<img width="1178" height="665" alt="image" src="https://github.com/user-attachments/assets/7dd366a3-b5f9-40e1-b385-8a5609819569" />

## Journey to 3D
As the main focus of this project was on the WFC algorithm, we took advantage of the Ursina game engine to render our 3D environments. Once we started experimenting with the algorithm's 3D extension, we quickly ran into a few problems. Firstly, we needed a way to input a 3D space. Wanting to reuse as much of our code as possible, we opted to layer images on top of each other. This way, we could create a bunch of images and then have the program combine them into a 3D scene. Additionally, we needed a way to classify transparency, that way our worlds could have interesting detail. To do this, the color (0,0,0) is mapped to the transparent color, so we avoid using pure black in any of our tile sets. Below is a visual of our general process: given 5 images, we layer them onto each other to gain the desired 3D scene.

<img width="756" height="562" alt="image" src="https://github.com/user-attachments/assets/ca3fd6c4-f47f-4f07-b389-375d203e1a8e" />

## Added Complexity
Adding an extra dimension makes the WFC algorithm more computationally intensive. Before, in most of our samples, there were about 60-100 states present given simple tile sets. However, when scaling up to 3D, the amount of states present jumps to between 300-1000. Just take a look at the example below: even a small 5x5x5 volume can contain a staggering amount of unique states.
​
<img width="518" height="551" alt="image" src="https://github.com/user-attachments/assets/8d90b3a7-b9b2-447c-a24d-dda76b13a60c" />

This not only makes WFC require more memory, but also slows down the propagation step, as often each tile only loses a few states each step. This means the propagation queue can get quite large and eventually run out of memory before all of the changes can be made. Our solution to this was to use a chunk-based system, which lets WFC run on smaller spaces at the expense that sometimes chunk boundaries can be illegal, which requires the whole generation to be restarted. However, the chunk-based approach overall runs faster and allows spaces to be extended over time. Here are a couple examples with the full-working 3D WFC:
    
<img width="667" height="664" alt="image" src="https://github.com/user-attachments/assets/284a62c8-f31e-4cda-975e-48f776642474" />
<img width="1187" height="665" alt="image" src="https://github.com/user-attachments/assets/77fbaec3-004d-4c74-b442-22c95476981a" />

## Issues with WFC

Overhangs and floating objects can give WFC quite some trouble. For example, below is a valid space generated by a sample containing trees. In the tile collection phase, the algorithm identified tiles that are mostly air with one voxel of leaf in them. In the adjacency calculation, the algorithm determines it is valid to put air below and above this tile. So, when it comes to generation, the algorithm is allowed to creating floating lines of leaves.

<img width="598" height="400" alt="image" src="https://github.com/user-attachments/assets/eddc936c-3aec-4fa5-bf43-56b6c513a21f" />

## Requirements

    Python

    Required libraries (install with pip):

    python -m pip install ursina
    python -m pip install numpy
    python -m pip install matplotlib
    python -m pip install jupyter
    
