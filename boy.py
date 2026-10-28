from pico2d import load_image, get_time
from transitions import Machine


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.idle_start_time = get_time()
        self.left_down = False
        self.right_down = False

        self.state_machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'SLEEP'],
            initial='IDLE',
            auto_transitions=False,
        )

        self.state_machine.add_transition(
            trigger='tick', source='IDLE', dest=None,
            after='animate_idle',
        )
        self.state_machine.add_transition(
            trigger='tick', source='RUN', dest=None,
            after='animate_run',
        )
        self.state_machine.add_transition(
            trigger='tick', source='SLEEP', dest=None,
            after='animate_sleep',
        )
        self.state_machine.add_transition(
            trigger='time_out', source='IDLE', dest='SLEEP',
            after='enter_sleep',
        )
        self.state_machine.add_transition(
            trigger='start_run', source=['IDLE', 'SLEEP'], dest='RUN',
            after='enter_run',
        )
        self.state_machine.add_transition(
            trigger='stop_run', source='RUN', dest='IDLE',
            after='enter_idle',
        )
        self.state_machine.add_transition(
            trigger='wake_up', source='SLEEP', dest='IDLE',
            after='enter_idle',
        )

    def update(self):
        self.tick()

        if self.state == 'RUN':
            direction = 0
            if self.left_down:
                direction -= 1
            if self.right_down:
                direction += 1

            self.x += direction * 5
            self.x = max(50, min(750, self.x))

        if self.state == 'IDLE' and get_time() - self.idle_start_time >= 5.0:
            self.time_out()

    def handle_event(self, event):
        from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT

        if event.type == SDL_KEYDOWN:
            if self.state == 'SLEEP' and event.key == SDLK_SPACE:
                self.wake_up()
                return

            if event.key == SDLK_LEFT:
                self.left_down = True
                self.face_dir = -1
                if self.state in ('IDLE', 'SLEEP'):
                    self.start_run()
            elif event.key == SDLK_RIGHT:
                self.right_down = True
                self.face_dir = 1
                if self.state in ('IDLE', 'SLEEP'):
                    self.start_run()

        elif event.type == SDL_KEYUP:
            if event.key == SDLK_LEFT:
                self.left_down = False
            elif event.key == SDLK_RIGHT:
                self.right_down = False

            if self.state == 'RUN' and not self.left_down and not self.right_down:
                self.stop_run()

    def enter_idle(self):
        self.idle_start_time = get_time()
        self.frame = 0

    def enter_run(self):
        self.frame = 0

    def enter_sleep(self):
        self.frame = 0

    def animate_idle(self):
        self.frame = (self.frame + 1) % 8

    def animate_run(self):
        self.frame = (self.frame + 1) % 8

    def animate_sleep(self):
        self.frame = (self.frame + 1) % 8

    def draw(self):
        if self.state == 'SLEEP':
            source_y = 300 if self.face_dir == 1 else 200
            sleep_angle = 3.141592 / 2 if self.face_dir == 1 else -3.141592 / 2
            self.image.clip_composite_draw(
                self.frame * 100, source_y, 100, 100,
                sleep_angle, '', self.x - 25, self.y - 25,
                100, 100,
            )
        elif self.state == 'RUN':
            if self.face_dir == 1:
                self.image.clip_draw(self.frame * 100, 100, 100, 100, self.x, self.y)
            else:
                self.image.clip_draw(self.frame * 100, 0, 100, 100, self.x, self.y)
        elif self.face_dir == 1:
            self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
        else:
            self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
