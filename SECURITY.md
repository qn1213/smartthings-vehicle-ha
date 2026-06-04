# 보안 정책

이 통합은 SmartThings OAuth 토큰을 Home Assistant 공식 SmartThings 통합에서 읽어 사용합니다. 저장소, 이슈, PR, 로그에 아래 정보를 올리지 마세요.

- Home Assistant 장기 액세스 토큰
- SmartThings/Samsung OAuth 토큰, 쿠키, 인증 코드
- 실제 SmartThings `deviceId`
- 차량 번호, VIN, 위치 정보, 집 주소
- 개인 서버 URL, Cloudflare Tunnel URL, 홈 네트워크 정보

## 취약점 제보

공개 이슈에는 민감 정보를 포함하지 말고, 재현 절차와 영향 범위만 요약해 주세요. 민감 정보가 필요한 보안 제보는 저장소 소유자에게 비공개 채널로 먼저 연락해 주세요.

## 차량 제어 안전

잠금 해제, 원격 시동, 공조 제어는 실제 물리 동작입니다. 이 통합은 설치 중 자동으로 차량 명령을 실행하지 않지만, Home Assistant 버튼이나 자동화에서 실행하면 SmartThings API로 실제 명령이 전송됩니다.
