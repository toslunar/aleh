import argparse

import atari_py
import numpy as np
import pyglet
from pyglet import gl


ACTIONS = np.array([
    [
        [7, 4, 9],
        [2, 0, 5],
        [6, 3, 8],
    ],
    [
        [15, 12, 17],
        [10,  1, 13],
        [14, 11, 16],
    ],
])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', type=str)
    args = parser.parse_args()

    screen_scale = 2
    info_width = 400
    info_size = 24

    ale = atari_py.ALEInterface()
    ale.loadROM(atari_py.get_game_path(args.name))
    ale_width, ale_height = ale.getScreenDims()
    score = 0

    key = pyglet.window.key
    keys = key.KeyStateHandler()

    def get_action():
        lr = 1
        ud = 1
        fire = 1 if keys[key.ENTER] else 0
        if keys[key.A]:
            lr -= 1
        if keys[key.D]:
            lr += 1
        if keys[key.W]:
            ud -= 1
        if keys[key.S]:
            ud += 1
        return ACTIONS[fire, lr, ud]

    def reset_game():
        nonlocal score
        ale.reset_game()
        score = 0

    def update(dt):
        nonlocal score
        action = get_action()
        score += ale.act(action)
        # print(score)
        if keys[key.R]:
            reset_game()
        screen = ale.getScreenRGB2()
        image = pyglet.image.ImageData(
            ale_width,
            ale_height,
            'RGB',
            np.flip(screen, axis=0).tobytes(),
        )
        image.scale = screen_scale
        texture = image.get_texture()
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        texture.width *= screen_scale
        texture.height *= screen_scale
        window.clear()
        texture.blit(0, 0)
        info_strs = [
            "score: {}".format(score),
            "lives: {}".format(ale.lives()),
            "frames: {}".format(ale.getFrameNumber()),
            "fps: {:.2f}".format(pyglet.clock.get_fps()),
        ]
        if ale.game_over():
            info_strs.append("game_over")
        label = pyglet.text.Label(
            "\n".join(info_strs),
            font_size=info_size,
            x=ale_width * screen_scale + 50, y=ale_height * screen_scale - 100,
            width=info_width - 100,
            color=(255, 255, 255, 255),
            multiline=True)
        label.draw()

    window = pyglet.window.Window(
        width=ale_width * screen_scale + info_width,
        height=ale_height * screen_scale)
    window.push_handlers(keys)
    pyglet.clock.schedule_interval(update, 1./60)
    pyglet.app.run()


if __name__ == '__main__':
    main()
