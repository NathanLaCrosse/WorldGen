Wave Function Collapse Project

Overview

This project uses the Wave Function Collapse (WFC) algorithm to generate worlds from a small sample input. It works by following rules that decide how pieces can fit together.


Requirements

    Python

    Required libraries (install with pip):

    python -m pip install ursina
    python -m pip install numpy
    python -m pip install matplotlib
    python -m pip install jupyter

Algorithm Basics

    - Analyze Tile Set​
    - Find Interlocking Patterns​
    - Determine Adjacency Rules​
    - Create a sample tile set based on tile size 
    - We use backtracking to handle if as WFC goes, there is a failure
    
<img width="263" height="267" alt="image" src="https://github.com/user-attachments/assets/36ed65db-5baa-4564-bac4-294966a1ebc0" />
<img width="393" height="258" alt="image" src="https://github.com/user-attachments/assets/1d31f022-dce4-43d0-ad84-34fd429220f7" />
<img width="498" height="504" alt="image" src="https://github.com/user-attachments/assets/15671864-419a-4e34-84b9-0ff2dcca3f2b" />


2D Generation and examples

    - How to use the 2D generation code here

<img width="1178" height="665" alt="image" src="https://github.com/user-attachments/assets/7dd366a3-b5f9-40e1-b385-8a5609819569" />

How 3D works

    - Uses a layered png style as shown here to create the image
    - Added in some constraints, like transperency which is treated as a color. 
        - Both above and below ground transparency to ensure that caves can be generated without floating stone in the sky
    - Ability to seed the starting tile to a specific tile for generation
<img width="756" height="562" alt="image" src="https://github.com/user-attachments/assets/ca3fd6c4-f47f-4f07-b389-375d203e1a8e" />


3D complexity

    - 3D addes in two more directions for adjecency list. 
    Far More States (~60 -> 300 - 1000)​
    
    Difficulty in Propagating State Changes​
<img width="518" height="551" alt="image" src="https://github.com/user-attachments/assets/8d90b3a7-b9b2-447c-a24d-dda76b13a60c" />

3D examples
    
<img width="667" height="664" alt="image" src="https://github.com/user-attachments/assets/284a62c8-f31e-4cda-975e-48f776642474" />
<img width="1187" height="665" alt="image" src="https://github.com/user-attachments/assets/77fbaec3-004d-4c74-b442-22c95476981a" />

Issues with WFC

    - has trouble with floating objects
<img width="598" height="400" alt="image" src="https://github.com/user-attachments/assets/eddc936c-3aec-4fa5-bf43-56b6c513a21f" />


    
