# PRD: Drill #11 소년 자동 무적 런(AutoRun) 상태 추가

## 1. 개요

LEC12 캐릭터 컨트롤러(IDLE, SLEEP, RUN 상태)에 **자동 무적 런(AutoRun)** 상태를 추가한다.
IDLE 상태에서 `a` 키를 누르면 소년이 키 조작 없이 화면 좌우를 자동으로 오가며 달린다.
AutoRun 중에는 더 빠르고 더 크게 보이며, 5초가 지나거나 방향키를 누르면 AutoRun이 끝난다.

## 2. 개발 환경

| 항목 | 내용 |
|---|---|
| 언어 | Python 3.13 |
| 그래픽 라이브러리 | pico2d |
| 상태 머신 라이브러리 | transitions 0.9.3 (`pip install transitions`) |
| 캔버스 | 800 × 600 (`open_canvas()` 기본 크기) |
| 스프라이트 | `animation_sheet.png` (프레임 100 × 100, 가로 8프레임) |
| 배경 | `grass.png` |

## 3. 파일 구성

| 파일 | 역할 |
|---|---|
| `main.py` | 게임 루프 (handle_events → update_world → render_world) |
| `boy.py` | 소년 클래스와 상태 클래스(Idle, Sleep, Run, AutoRun), 상태 머신 |
| `glass.py` | 잔디(Grass) 클래스 |
| `animation_sheet.png`, `grass.png` | 실행에 필요한 이미지 |
| `state_diagram.png` | 상태 다이어그램 |
| `PRD.md` | 이 문서 |

## 4. 기존 기능 (LEC12에서 구현한 것, 유지)

- IDLE: 제자리 대기 애니메이션. 5초 동안 입력이 없으면 SLEEP.
- SLEEP: 누워서 자는 모습. SPACE를 누르면 IDLE, 방향키를 누르면 RUN.
- RUN: 방향키를 누르는 동안 그 방향으로 달림. 방향키를 모두 떼면 IDLE.
- 왼쪽/오른쪽은 별도 상태가 아니라 하나의 RUN 상태에서 `dir` 값으로 구분.
- 화면 밖으로 나가지 않음.
- 애니메이션 프레임은 시간 기준(0.05초에 한 장)으로 넘김.

## 5. 추가 기능 요구사항 (AutoRun)

| 번호 | 요구사항 |
|---|---|
| FR-1 | IDLE 상태에서 `a` 키를 누르면 AUTO_RUN 상태가 된다. |
| FR-2 | AUTO_RUN에서는 키 조작 없이 계속 좌우로 이동한다. 처음에는 바라보던 방향으로 출발한다. |
| FR-3 | AUTO_RUN에서는 RUN보다 이동 속도가 빠르다. |
| FR-4 | AUTO_RUN에서는 소년의 크기가 확대된다. 발 위치(바닥선)는 그대로 유지한다. |
| FR-5 | 화면 좌우 끝에 닿으면 자동으로 방향을 바꾼다. 확대된 이미지가 화면 밖으로 나가지 않는다. |
| FR-6 | AUTO_RUN 상태로 5초 이상 지나면 IDLE 상태로 돌아간다. |
| FR-7 | AUTO_RUN 중 방향키를 누르면 AutoRun이 취소되고, 눌린 방향으로 움직이는 RUN 상태가 된다. |
| FR-8 | AutoRun은 반드시 별도의 상태 클래스(`AutoRun`)로 구현한다. |
| FR-9 | 상태 다이어그램을 이미지 파일로 저장소에 포함한다. |

## 6. 상태 설계

각 상태는 transitions의 `State`를 상속한 `BoyState` 클래스를 부모로 하는 **상태 클래스**로 만든다.

| 메서드 | 호출 시점 |
|---|---|
| `on_enter_state(boy)` | 상태에 들어갈 때 (Entry action) |
| `on_exit_state(boy)` | 상태에서 나갈 때 (Exit action) |
| `do(boy)` | 상태에 머무는 동안 매 프레임 (Do activity) |
| `draw(boy)` | 그리기 |

### 6.1 상태 목록

| 상태 | 클래스 | 하는 일 |
|---|---|---|
| IDLE | `Idle` | 대기 애니메이션, 5초 타이머 |
| SLEEP | `Sleep` | 누워서 자는 모습 |
| RUN | `Run` | 방향키 방향으로 이동 |
| AUTO_RUN | `AutoRun` | 자동 좌우 이동, 빠른 속도, 2배 크기, 5초 타이머 |

### 6.2 상태 전환

| 출발 | 이벤트 (trigger) | 도착 |
|---|---|---|
| IDLE | `time_out` (IDLE로 5초 경과) | SLEEP |
| SLEEP | `space_down` (SPACE) | IDLE |
| IDLE, SLEEP | `run_start` (←/→ 누름) | RUN |
| RUN | `run_stop` (←/→ 모두 뗌) | IDLE |
| IDLE | `a_down` (`a` 누름) | AUTO_RUN |
| AUTO_RUN | `auto_run_time_out` (AUTO_RUN으로 5초 경과) | IDLE |
| AUTO_RUN | `run_start` (←/→ 누름) | RUN |

그 상태에 정의되지 않은 이벤트는 무시한다(`ignore_invalid_triggers=True`). 예: SLEEP에서 `a`, RUN에서 `a`.
