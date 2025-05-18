# n8n Docker Setup

이 프로젝트는 n8n을 Docker를 사용하여 실행하기 위한 설정을 포함하고 있습니다.

## 사전 요구사항

- Docker
- Docker Compose

## 실행 방법

1. 프로젝트를 클론합니다
2. 다음 명령어로 n8n을 실행합니다:
   ```bash
   docker-compose up -d
   ```

## 접속 방법

- URL: http://localhost:5678
- 기본 계정:
  - 사용자: admin
  - 비밀번호: password

## 환경 변수 설정

`docker-compose.yml` 파일에서 다음 환경 변수들을 수정할 수 있습니다:

- N8N_BASIC_AUTH_USER: 관리자 계정 사용자명
- N8N_BASIC_AUTH_PASSWORD: 관리자 계정 비밀번호
- TZ: 타임존 설정

## 데이터 저장

모든 n8n 데이터는 Docker 볼륨 `n8n_data`에 저장됩니다. 