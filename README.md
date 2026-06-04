# 스마트싱스 차량 Home Assistant 통합

한국 SmartThings 계정에 연결된 현대자동차·기아·제네시스 차량을 Home Assistant에서 조회하고, 사용자가 명시적으로 누른 차량 제어를 실행하기 위한 커스텀 통합입니다.

이 프로젝트는 **한국 사용 환경 전용**으로 설계합니다. 현재 목표는 한국 SmartThings에서 보이는 현대차그룹 차량이 Home Assistant 공식 SmartThings 통합에는 차량 엔티티로 노출되지 않는 문제를 보완하는 것입니다.

## 현재 상태

초기 공개 배포 준비 버전입니다.

검증된 흐름:

- Home Assistant 공식 SmartThings 통합의 OAuth 토큰 재사용
- SmartThings REST API 차량 상태 조회
- SmartThings 차량 자동 탐색 기반 설정 화면
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

`공조 켜기` 버튼은 아래 UI 엔티티 값을 읽어 SmartThings에 전송합니다.

- 공조 설정 온도: 17–27℃, 기본 22℃
- 공조 작동 시간: 1–30분, 기본 10분
- 앞유리 김서림 제거: `off` / `on`, 기본 `off`

창문 상태는 조회만 가능합니다. 현재 SmartThings capability 정의상 `vehicleWindowState`에는 창문 열기/닫기 명령이 없습니다.

## 설치 전 준비

먼저 Home Assistant에 공식 SmartThings 통합이 설정되어 있어야 합니다.

1. Home Assistant → 설정 → 기기 및 서비스
2. SmartThings 공식 통합 추가
3. 삼성 계정 로그인 및 승인 완료
4. SmartThings에 차량이 보이는지 확인

이 커스텀 통합은 위 공식 통합의 OAuth 토큰을 재사용합니다.

## HACS 설치

공개 저장소 배포 기준의 권장 설치 방법입니다.

1. Home Assistant에 [HACS](https://hacs.xyz/)를 설치하고 GitHub 인증을 완료합니다.
2. HACS → 통합 → 우측 상단 메뉴 → 사용자 정의 저장소를 엽니다.
3. 저장소 URL에 아래 주소를 입력합니다.

   ```text
   https://github.com/gomeng-dev/smartthings-vehicle-ha
   ```

4. 카테고리는 `Integration`을 선택합니다.
5. `스마트싱스 차량`을 다운로드합니다.
6. Home Assistant를 재시작합니다.

## 수동 설치

HACS를 쓰지 않는 경우 다음처럼 설치할 수 있습니다.

```bash
cd ~/.homeassistant
mkdir -p custom_components
cp -R /path/to/smartthings-vehicle-ha/custom_components/smartthings_vehicle custom_components/
```

그다음 Home Assistant를 재시작합니다.

```bash
launchctl kickstart -k gui/$(id -u)/com.homeassistant.core
```

## 최초 설정 / 온보딩

Home Assistant 재시작 후:

1. 설정 → 기기 및 서비스
2. 통합 추가
3. `스마트싱스 차량` 검색
4. 자동 탐색된 차량 목록에서 차량 선택
5. 차량 이름 확인 또는 수정
6. 설정 완료

설정 화면은 Home Assistant 공식 SmartThings 통합의 OAuth 토큰을 사용해 SmartThings `/devices` 목록을 조회하고, `vehicle*` capability가 있는 장치를 차량 후보로 보여줍니다.

자동 탐색에 실패하거나 차량 후보가 없으면 `SmartThings 차량` 입력칸에 SmartThings 차량 장치 ID를 직접 입력할 수 있습니다.

설정 완료 후에는 고위험 제어를 포함한 모든 차량 제어 엔티티가 생성됩니다.

- 차량 상태 새로고침
- 차량 연결 확인
- 차량 잠금
- 차량 잠금 해제
- 원격 시동 켜기 / 끄기
- 공조 켜기 / 끄기

잠금 해제, 원격 시동, 공조 제어는 실제 차량 상태를 바꾸는 동작입니다. 이 통합은 설치/검증 과정에서 이런 명령을 자동 실행하지 않지만, 생성된 버튼을 누르거나 자동화에 넣으면 실제 명령이 전송됩니다.

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
