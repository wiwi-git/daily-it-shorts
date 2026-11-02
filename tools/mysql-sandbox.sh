#!/usr/bin/env bash
# 예제 쿼리 검증용 임시 MySQL 컨테이너. build.py가 `docker exec`로 접속해 쿼리를 실행한다.
#   tools/mysql-sandbox.sh start   # 없으면 띄우고 접속 가능할 때까지 대기
#   tools/mysql-sandbox.sh stop    # 컨테이너 삭제(--rm)
set -euo pipefail
NAME=shorts-mysql
# 검증 결과(DESC·SHOW GRANTS 문자열 등)가 버전에 따라 달라지지 않도록 이미지를 고정한다
IMAGE=${MYSQL_IMAGE:-mysql:26.10.0@sha256:f51c9c01c16b0eb5d81bb70ab7e7fcb3b96abc6a54114be3a94e8e569cae7815}

case "${1:-start}" in
  start)
    if [ -z "$(docker ps -q -f name="^${NAME}$")" ]; then
      docker run -d --rm --name "$NAME" -e MYSQL_ROOT_PASSWORD=sandbox "$IMAGE" >/dev/null
    fi
    # 이미지 초기화 중에는 임시 서버가 한 번 떴다 내려가므로, 3306 포트로 뜬 최종 서버를 기다린다
    until docker logs "$NAME" 2>&1 | grep -q "ready for connections.*port: 3306"; do sleep 1; done
    docker exec "$NAME" mysql -uroot -psandbox -N -e "SELECT VERSION()" 2>/dev/null
    ;;
  stop)
    docker stop "$NAME" >/dev/null && echo stopped
    ;;
esac
