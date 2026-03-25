from ursina import *
# from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# player = FirstPersonController()

from ursina.prefabs.editor_camera import EditorCamera

EditorCamera()

for x in range(5):
    for y in range(5):
        for z in range(5):
            Entity(model='cube', position=(x,y,z), color=color.rfandom_color())

def input(key):
    if key == 'escape':
        application.quit()

app.run()