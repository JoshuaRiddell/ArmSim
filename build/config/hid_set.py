import pyglet

window = pyglet.window.Window()

label = pyglet.text.Label('Press a key',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')


@window.event
def on_draw():
    window.clear()
    label.draw()


@window.event
def on_key_press(symbol, modifiers):
    label.text = "Mod: " + str(int(modifiers))


@window.event
def on_key_release(symbol, modifiers):
    label.text = "Mod: " + str(int(modifiers))

pyglet.app.run()
