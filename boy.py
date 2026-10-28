from pico2d import load_image, get_time, clamp
from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_RIGHT, SDLK_LEFT
from transitions import Machine, State

FRAME_INTERVAL = 0.05     # 프레임 한 장을 보여주는 시간(초). 클수록 다리가 천천히 움직임
RUN_SPEED = 5             # RUN 이동 속도 (한 번 갱신할 때 움직이는 픽셀)
SLEEP_WAIT_TIME = 5       # IDLE로 이 시간(초)이 지나면 SLEEP


class BoyState(State):
    """소년 상태의 공통 부모 클래스.
    enter: 상태에 들어갈 때, exit: 나갈 때, do: 머무는 동안 매 프레임, draw: 그리기"""
    frame_interval = FRAME_INTERVAL

    def enter(self, event_data):
        super().enter(event_data)
        self.on_enter_state(event_data.model)

    def exit(self, event_data):
        super().exit(event_data)
        self.on_exit_state(event_data.model)

    def on_enter_state(self, boy):
        pass

    def on_exit_state(self, boy):
        pass

    def do(self, boy):
        pass

    def draw(self, boy):
        pass


class Idle(BoyState):
    def __init__(self):
        super().__init__('IDLE')

    def on_enter_state(self, boy):
        boy.idle_start_time = get_time()    # IDLE에 들어올 때마다 5초 타이머 다시 시작

    def do(self, boy):
        if boy.dir != 0:                    # SLEEP에서 깨어날 때 방향키를 누르고 있던 경우
            boy.run_start()
        elif get_time() - boy.idle_start_time >= SLEEP_WAIT_TIME:
            boy.time_out()

    def draw(self, boy):
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * 100, 300, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, 200, 100, 100, boy.x, boy.y)


class Sleep(BoyState):
    def __init__(self):
        super().__init__('SLEEP')

    def draw(self, boy):
        # 대기 프레임을 90도 눕혀서 그림
        if boy.face_dir == 1:
            boy.image.clip_composite_draw(boy.frame * 100, 300, 100, 100,
                                          3.141592 / 2, '', boy.x - 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, 200, 100, 100,
                                          -3.141592 / 2, '', boy.x + 25, boy.y - 25, 100, 100)


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1        # 바라보는 방향: 1 오른쪽, -1 왼쪽
        self.dir = 0             # 이동 방향: 1 오른쪽, -1 왼쪽, 0 정지
        self.image = load_image('animation_sheet.png')
        self.idle_start_time = get_time()   # IDLE에 들어간 시각 (5초 타이머 기준)
        self.frame_time = get_time()        # 마지막으로 프레임을 넘긴 시각

        # 상태: IDLE, SLEEP, RUN (왼쪽/오른쪽은 하나의 RUN 상태)
        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP', 'RUN'],
            transitions=[
                {'trigger': 'time_out', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'space_down', 'source': 'SLEEP', 'dest': 'IDLE'},
                {'trigger': 'run_start', 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
                {'trigger': 'run_stop', 'source': 'RUN', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
            ignore_invalid_triggers=True,   # 그 상태에 없는 전환은 오류 없이 무시
        )

    # IDLE 상태로 들어올 때마다 자동 호출 -> 5초 타이머 다시 시작
    def on_enter_IDLE(self):
        self.idle_start_time = get_time()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT:
                self.dir += 1
            elif event.key == SDLK_LEFT:
                self.dir -= 1
            elif event.key == SDLK_SPACE:
                self.space_down()
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                self.dir -= 1
            elif event.key == SDLK_LEFT:
                self.dir += 1

        if self.dir != 0:
            self.run_start()     # IDLE 또는 SLEEP에서 RUN으로 바뀜
        else:
            self.run_stop()      # RUN에서만 IDLE로 바뀜

    def update(self):
        # 갱신 횟수가 아니라 시간 기준으로 프레임을 넘김 (delay 값과 상관없이 같은 속도)
        if get_time() - self.frame_time >= FRAME_INTERVAL:
            self.frame = (self.frame + 1) % 8
            self.frame_time = get_time()

        if self.state == 'IDLE':
            if self.dir != 0:                       # SLEEP에서 깨어날 때 방향키를 누르고 있던 경우
                self.run_start()
            elif get_time() - self.idle_start_time >= SLEEP_WAIT_TIME:
                self.time_out()
        elif self.state == 'RUN':
            self.face_dir = self.dir
            self.x += self.dir * RUN_SPEED
            self.x = clamp(50, self.x, 800 - 50)    # 화면 밖으로 나가지 않게 (이미지 폭의 절반만큼 여백)

    def draw(self):
        if self.state == 'IDLE':
            if self.face_dir == 1:
                self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
            else:
                self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
        elif self.state == 'RUN':
            if self.face_dir == 1:
                self.image.clip_draw(self.frame * 100, 100, 100, 100, self.x, self.y)
            else:
                self.image.clip_draw(self.frame * 100, 0, 100, 100, self.x, self.y)
        elif self.state == 'SLEEP':
            # 대기 프레임을 90도 눕혀서 그림
            if self.face_dir == 1:
                self.image.clip_composite_draw(self.frame * 100, 300, 100, 100,
                                               3.141592 / 2, '', self.x - 25, self.y - 25, 100, 100)
            else:
                self.image.clip_composite_draw(self.frame * 100, 200, 100, 100,
                                               -3.141592 / 2, '', self.x + 25, self.y - 25, 100, 100)
