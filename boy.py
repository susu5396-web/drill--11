from pico2d import load_image, get_time
from transitions import Machine


class AutoRun:
    """Auto Run 상태의 이동, 지속 시간, 크기 동작을 담당한다."""

    SPEED = 10
    DRAW_SIZE = 150

    def __init__(self):
        self.direction = 1
        self.start_time = 0.0

    def enter(self, boy):
        self.start_time = get_time()
        self.direction = boy.face_dir
        boy.frame = 0

    def update(self, boy):
        boy.x += self.direction * self.SPEED
        half_size = self.DRAW_SIZE // 2

        if boy.x <= half_size:
            boy.x = half_size
            self.direction = 1
            boy.face_dir = 1
        elif boy.x >= 800 - half_size:
            boy.x = 800 - half_size
            self.direction = -1
            boy.face_dir = -1

        if get_time() - self.start_time >= 5.0:
            boy.stop_auto_run()

    def draw(self, boy):
        source_y = 100 if boy.face_dir == 1 else 0
        boy.image.clip_draw(
            boy.frame * 100, source_y, 100, 100,
            boy.x, boy.y, self.DRAW_SIZE, self.DRAW_SIZE,
        )


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.idle_start_time = get_time()
        self.left_down = False
        self.right_down = False
        self.auto_run_state = AutoRun()

        self.state_machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'AUTO_RUN', 'SLEEP'],
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
            trigger='tick', source='AUTO_RUN', dest=None,
            after='animate_auto_run',
        )
        self.state_machine.add_transition(
            trigger='time_out', source='IDLE', dest='SLEEP',
            after='enter_sleep',
        )
        self.state_machine.add_transition(
            trigger='start_run', source=['IDLE', 'SLEEP', 'AUTO_RUN'], dest='RUN',
            after='enter_run',
        )
        self.state_machine.add_transition(
            trigger='stop_run', source='RUN', dest='IDLE',
            after='enter_idle',
        )
        self.state_machine.add_transition(
            trigger='start_auto_run', source='IDLE', dest='AUTO_RUN',
            after='enter_auto_run',
        )
        self.state_machine.add_transition(
            trigger='stop_auto_run', source='AUTO_RUN', dest='IDLE',
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

        if self.state == 'AUTO_RUN':
            self.auto_run_state.update(self)

        if self.state == 'IDLE' and get_time() - self.idle_start_time >= 5.0:
            self.time_out()

    def handle_event(self, event):
        from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_a, SDLK_LEFT, SDLK_RIGHT

        if event.type == SDL_KEYDOWN:
            if self.state == 'SLEEP' and event.key == SDLK_SPACE:
                self.wake_up()
                return

            if self.state == 'IDLE' and event.key == SDLK_a:
                self.start_auto_run()
                return

            if event.key == SDLK_LEFT:
                self.left_down = True
                self.face_dir = -1
                if self.state in ('IDLE', 'SLEEP', 'AUTO_RUN'):
                    self.start_run()
            elif event.key == SDLK_RIGHT:
                self.right_down = True
                self.face_dir = 1
                if self.state in ('IDLE', 'SLEEP', 'AUTO_RUN'):
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

    def enter_auto_run(self):
        self.auto_run_state.enter(self)

    def enter_sleep(self):
        self.frame = 0

    def animate_idle(self):
        self.frame = (self.frame + 1) % 8

    def animate_run(self):
        self.frame = (self.frame + 1) % 8

    def animate_auto_run(self):
        self.frame = (self.frame + 1) % 8

    def animate_sleep(self):
        self.frame = (self.frame + 1) % 8

    def draw(self):
        if self.state == 'AUTO_RUN':
            self.auto_run_state.draw(self)
        elif self.state == 'SLEEP':
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
