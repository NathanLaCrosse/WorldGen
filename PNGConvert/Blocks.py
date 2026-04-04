"""----------------------------------------------------------------

Simple block creation code to allow dynamic creation of blocks.
Only used for sample block display. 

Dylan Dudley - 03/27/2026

----------------------------------------------------------------"""

from ursina import *

def create_block(position=(0,0,0), color=color.white):
    return Entity(
        model='cube',
        color=color,
        position=position,
        scale=(1, 1, 1)
        
    )