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
