# 스마트싱스 차량 Home Assistant 통합

한국 SmartThings 계정에 연결된 현대자동차·기아·제네시스 차량을 Home Assistant에서 조회하고, 사용자가 명시적으로 누른 차량 제어를 실행하기 위한 커스텀 통합입니다.

이 프로젝트는 **한국 사용 환경 전용**으로 설계합니다. 현재 목표는 한국 SmartThings에서 보이는 현대차그룹 차량이 Home Assistant 공식 SmartThings 통합에는 차량 엔티티로 노출되지 않는 문제를 보완하는 것입니다.

## 현재 상태

초기 개발 버전입니다.

검증된 흐름:

- Home Assistant 공식 SmartThings 통합의 OAuth 토큰 재사용
- SmartThings REST API 차량 상태 조회
- `쏘나타` 차량에서 도어 잠금/해제 명령의 실제 상태 변화 확인
- Home Assistant Core macOS 환경에서 모듈 import 확인
- GitHub Actions CI 통과

## 설계 원칙

- **한국어 우선**: README, 설정 화면, 엔티티 이름 등 사용자가 보는 인터페이스는 한국어로 작성합니다.
- **한국 전용**: 한국 SmartThings와 현대차그룹 차량 연동을 기준으로 동작을 설계합니다.
- **안전 우선**: 차량 제어는 기본적으로 보수적으로 노출합니다.
- **공식 API 우선**: Chrome 자동화나 웹 스크래핑보다 SmartThings REST API 경로를 우선합니다.
- **기존 인증 재사용**: 사용자가 별도 토큰을 붙여 넣지 않도록 Home Assistant 공식 SmartThings 통합의 OAuth 세션을 재사용합니다.

## 제공 예정 기능

### 상태 센서

- 주행 가능 거리
- 누적 주행 거리
- 시동 상태
- 공조 상태
- 실내 온도
- 도어 잠금 상태
- 각 도어 상태
- 각 창문 상태
- 연료 경고
- 스마트키 배터리 상태
- SmartThings 장치 온라인 상태

### 제어 버튼

SmartThings REST API가 이 차량에서 명령으로 노출한 제어 기능:

- 차량 상태 새로고침
- 차량 연결 확인
- 차량 잠금
- 차량 잠금 해제
- 원격 시동 켜기
- 원격 시동 끄기
- 공조 켜기
- 공조 끄기

`공조 켜기` 버튼은 현재 기본값으로 `22℃`, `10분`, `앞유리 김서림 제거 off`를 전송합니다. 세부 온도/시간 선택 UI는 추후 별도 엔티티나 서비스로 확장할 수 있습니다.

창문 상태는 조회만 가능합니다. 현재 SmartThings capability 정의상 `vehicleWindowState`에는 창문 열기/닫기 명령이 없습니다.

## 설치 전 준비

먼저 Home Assistant에 공식 SmartThings 통합이 설정되어 있어야 합니다.

1. Home Assistant → 설정 → 기기 및 서비스
2. SmartThings 공식 통합 추가
3. 삼성 계정 로그인 및 승인 완료
4. SmartThings에 차량이 보이는지 확인

이 커스텀 통합은 위 공식 통합의 OAuth 토큰을 재사용합니다.

## 수동 설치

아직 정식 HACS 배포 전이라면 다음처럼 설치할 수 있습니다.

```bash
cd ~/.homeassistant
mkdir -p custom_components
cp -R /path/to/smartthings-vehicle-ha/custom_components/smartthings_vehicle custom_components/
```

그다음 Home Assistant를 재시작합니다.

```bash
launchctl kickstart -k gui/$(id -u)/com.homeassistant.core
```

## 설정

Home Assistant 재시작 후:

1. 설정 → 기기 및 서비스
2. 통합 추가
3. `스마트싱스 차량` 검색
4. SmartThings 차량 장치 ID 입력
5. 차량 이름 입력

현재 검증에 사용한 SmartThings 차량 장치 ID는 개발 환경에서만 사용하며, README에는 실제 ID를 공개하지 않습니다.

## 보안과 안전

차량 제어는 실제 물리 동작을 일으킬 수 있습니다.

이 프로젝트의 기본 정책:

- 상태 조회는 자동으로 허용
- 모든 제어 기능은 사용자가 Home Assistant에서 명시적으로 누르는 버튼으로만 실행
- 잠금 해제, 공조, 원격 시동은 실제 차량 상태를 바꾸는 고위험 동작이므로 자동화에 넣을 때 조건을 보수적으로 설정해야 함
- 이 통합은 설치/검증 과정에서 고위험 제어 명령을 자동 실행하지 않음

## 개발

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pip install ruff
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m compileall -q custom_components tests
```

## 라이선스

MIT
