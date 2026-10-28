from pico2d import load_image #피코투디로부터 로드 이미지를 가져오겠다?

class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def draw(self):
        self.image.draw(400, 30)

    def update(self):
        pass

