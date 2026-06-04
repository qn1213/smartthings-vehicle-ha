# 스마트싱스 차량

[![GitHub release](https://img.shields.io/github/v/release/gomeng-dev/smartthings-vehicle-ha?display_name=tag)](https://github.com/gomeng-dev/smartthings-vehicle-ha/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)
[![CI](https://github.com/gomeng-dev/smartthings-vehicle-ha/actions/workflows/ci.yml/badge.svg)](https://github.com/gomeng-dev/smartthings-vehicle-ha/actions/workflows/ci.yml)

한국 SmartThings에 등록된 현대자동차·기아·제네시스 차량을 Home Assistant에서 조회하고 제어하는 커스텀 통합입니다.

Home Assistant 공식 SmartThings 통합의 OAuth 인증을 재사용하므로, 별도 토큰을 복사하거나 붙여 넣을 필요가 없습니다.

## 주요 기능

- SmartThings 차량 자동 탐색
- 주행 가능 거리, 누적 주행 거리, 시동, 공조, 잠금, 도어, 창문, 연료 경고, 스마트키 배터리, 연결 상태 조회
- 차량 상태 새로고침 및 연결 확인
- 차량 잠금 / 잠금 해제는 잠금 엔티티로 제어
- SmartThings 앱처럼 원격 시동은 별도 스위치로 노출하지 않고 공조 켜기 / 끄기 스위치로 함께 관리
- 공조 온도, 작동 시간, 앞유리 김서림 제거 설정

## 지원 환경

- Home Assistant 2024.12.0 이상
- HACS
- Home Assistant 공식 SmartThings 통합
- 한국 SmartThings 계정에 등록된 현대자동차·기아·제네시스 차량

## 설치 전 준비

먼저 Home Assistant에 공식 SmartThings 통합을 설정하세요.

1. Home Assistant → 설정 → 기기 및 서비스
2. 통합 추가 → SmartThings
3. 삼성 계정 로그인 및 권한 승인
4. SmartThings 앱 또는 Home Assistant에서 차량이 계정에 등록되어 있는지 확인

## HACS 설치

아직 HACS 기본 저장소에 포함되지 않은 경우 사용자 정의 저장소로 추가합니다.

1. HACS → 통합
2. 우측 상단 메뉴 → 사용자 정의 저장소
3. 저장소 URL 입력

   ```text
   https://github.com/gomeng-dev/smartthings-vehicle-ha
   ```

4. 카테고리 `Integration` 선택
5. `스마트싱스 차량` 다운로드
6. Home Assistant 재시작

## 최초 설정

Home Assistant를 재시작한 뒤 통합을 추가합니다.

1. 설정 → 기기 및 서비스
2. 통합 추가
3. `스마트싱스 차량` 검색
4. 자동 탐색된 차량 목록에서 차량 선택
5. 차량 이름 확인 또는 수정
6. 설정 완료

자동 탐색된 차량이 없으면 SmartThings 차량 장치 ID를 직접 입력할 수 있습니다.

## 생성되는 엔티티

### 센서

- 주행 가능 거리
- 누적 주행 거리
- 시동 상태
- 공조 상태
- 실내 온도
- 잠금 상태
- 운전석 / 조수석 / 뒤 좌측 / 뒤 우측 도어
- 운전석 / 조수석 / 뒤 좌측 / 뒤 우측 창문
- 연료 경고
- 스마트키 배터리
- 연결 상태

### 버튼

- 차량 상태 새로고침
- 차량 연결 확인

### 잠금

- 차량 잠금: 잠금 / 잠금 해제

### 스위치

- 공조: 켜기 / 끄기. 켜기 명령에는 설정된 작동 시간이 포함되어 SmartThings 차량 원격 공조처럼 시동과 공조가 함께 동작합니다.

### 공조 설정

- 공조 설정 온도: 17–27℃, 기본 22℃
- 공조 작동 시간: 1–30분, 기본 10분
- 앞유리 김서림 제거: `off` / `on`, 기본 `off`

`공조` 스위치를 켜면 현재 설정된 공조 값과 작동 시간이 SmartThings로 전송됩니다. 온도나 작동 시간을 바꾸는 것만으로는 차량 명령이 실행되지 않습니다.

## 안전 안내

차량 제어는 실제 차량 상태를 바꾸는 동작입니다.

- 잠금 해제와 공조 제어는 신중하게 사용하세요. 공조 켜기는 차량 원격 공조 동작으로, 설정된 작동 시간 동안 차량 시동/공조가 함께 동작할 수 있습니다.
- 자동화에 차량 제어를 넣을 때는 위치, 시간, 재실 여부 등 안전 조건을 함께 설정하는 것을 권장합니다.
- 설치 및 설정 과정에서는 차량 제어 명령이 자동으로 실행되지 않습니다.
- 창문은 현재 상태 조회만 지원합니다. SmartThings capability에 창문 열기/닫기 명령이 제공되지 않아 제어 버튼을 만들지 않습니다.

## 문제 해결

### SmartThings 차량 통합이 검색되지 않음

- HACS 설치 후 Home Assistant를 재시작했는지 확인하세요.
- `custom_components/smartthings_vehicle` 경로에 통합 파일이 설치되었는지 확인하세요.

### SmartThings에 연결할 수 없다는 오류가 표시됨

- 공식 SmartThings 통합이 먼저 설정되어 있어야 합니다.
- 공식 SmartThings 통합의 삼성 계정 로그인이 만료되지 않았는지 확인하세요.
- Home Assistant를 재시작한 뒤 다시 시도하세요.

### 차량이 자동 탐색되지 않음

- SmartThings 앱에서 차량이 같은 삼성 계정에 등록되어 있는지 확인하세요.
- 공식 SmartThings 통합이 해당 계정으로 로그인되어 있는지 확인하세요.
- 필요한 경우 SmartThings 차량 장치 ID를 직접 입력하세요.

### 버튼/토글을 눌러도 차량 상태가 바로 바뀌지 않음

SmartThings 차량 명령은 네트워크, 차량 통신 상태, 제조사 서버 상태에 따라 반영까지 시간이 걸릴 수 있습니다. 잠시 기다린 뒤 `차량 상태 새로고침`을 눌러 확인하세요.

## 수동 설치

HACS를 사용하지 않는 경우 아래 경로에 통합 폴더를 복사합니다.

```bash
cd ~/.homeassistant
mkdir -p custom_components
cp -R /path/to/smartthings-vehicle-ha/custom_components/smartthings_vehicle custom_components/
```

복사 후 Home Assistant를 재시작하세요.

## 라이선스

MIT
