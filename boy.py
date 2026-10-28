from pico2d import load_image, get_time, clamp
from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_RIGHT, SDLK_LEFT, SDLK_a
from transitions import Machine, State

FRAME_INTERVAL = 0.05     # 프레임 한 장을 보여주는 시간(초). 클수록 다리가 천천히 움직임
RUN_SPEED = 5             # RUN 이동 속도 (한 번 갱신할 때 움직이는 픽셀)
SLEEP_WAIT_TIME = 5       # IDLE로 이 시간(초)이 지나면 SLEEP

AUTO_RUN_SPEED = 15       # AutoRun 이동 속도 (RUN의 3배)


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


class Run(BoyState):
    def __init__(self):
        super().__init__('RUN')

    def do(self, boy):
        boy.face_dir = boy.dir
        boy.x += boy.dir * RUN_SPEED
        boy.x = clamp(50, boy.x, 800 - 50)      # 화면 밖으로 나가지 않게 (이미지 폭의 절반만큼 여백)

    def draw(self, boy):
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * 100, 100, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, 0, 100, 100, boy.x, boy.y)


class AutoRun(BoyState):
    """자동 무적 런: 키 조작 없이 좌우로 계속 달림. 더 빠르다."""
    frame_interval = FRAME_INTERVAL / 2     # 다리도 RUN보다 2배 빠르게

    def __init__(self):
        super().__init__('AUTO_RUN')

    def on_enter_state(self, boy):
        boy.auto_dir = boy.face_dir            # 바라보던 방향으로 출발

    def do(self, boy):
        boy.x += boy.auto_dir * AUTO_RUN_SPEED
        # 화면 좌우 끝에 닿으면 자동으로 방향 전환
        if boy.x >= 800 - 50:
            boy.x = 800 - 50
            boy.auto_dir = -1
        elif boy.x <= 50:
            boy.x = 50
            boy.auto_dir = 1
        boy.face_dir = boy.auto_dir

    def draw(self, boy):
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * 100, 100, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, 0, 100, 100, boy.x, boy.y)


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1        # 바라보는 방향: 1 오른쪽, -1 왼쪽
        self.dir = 0             # 방향키 입력 상태: 1 오른쪽, -1 왼쪽, 0 없음
        self.auto_dir = 1        # AutoRun 이동 방향
        self.image = load_image('animation_sheet.png')
        self.idle_start_time = get_time()   # IDLE에 들어간 시각 (5초 타이머 기준)
        self.frame_time = get_time()        # 마지막으로 프레임을 넘긴 시각

        # 상태: 각 상태는 BoyState를 상속한 클래스 (왼쪽/오른쪽은 하나의 RUN 상태)
        self.machine = Machine(
            model=self,
            states=[Idle(), Sleep(), Run(), AutoRun()],
            transitions=[
                {'trigger': 'time_out', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'space_down', 'source': 'SLEEP', 'dest': 'IDLE'},
                {'trigger': 'run_start', 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
                {'trigger': 'run_stop', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'a_down', 'source': 'IDLE', 'dest': 'AUTO_RUN'},
            ],
            initial='IDLE',
            auto_transitions=False,
            ignore_invalid_triggers=True,   # 그 상태에 없는 전환은 오류 없이 무시
        )

    def cur_state(self):
        return self.machine.get_state(self.state)

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT:
                self.dir += 1
            elif event.key == SDLK_LEFT:
                self.dir -= 1
            elif event.key == SDLK_SPACE:
                self.space_down()
            elif event.key == SDLK_a:
                self.a_down()         # IDLE에서만 AUTO_RUN으로 바뀜
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
        if get_time() - self.frame_time >= self.cur_state().frame_interval:
            self.frame = (self.frame + 1) % 8
            self.frame_time = get_time()
        self.cur_state().do(self)

    def draw(self):
        self.cur_state().draw(self)
