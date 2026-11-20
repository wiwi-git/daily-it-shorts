# 작업지침

* 일반적인 작업 흐름
   * `/setup-matt-pocock-skills`: 최초 한번
   * `/grill-with-docs`: 큰 작업을 기획할 때
   * `/to-spec`
   * `/to-tickets`
   * `/implement-spec`
   * `/retro`
* 간단한 작업은 위 흐름을 타지 않아도 된다.
* 영상 티켓은 워크트리·병렬 에이전트 없이 메인 폴더에서 순서대로 구현한다. 한 영상의 티켓이 모두 같은 `build.py`를 고치고, 음성(mp3)은 커밋되지 않아 워크트리마다 다시 만들어야 하며, 빌드 결과물(`index.html`·`examples.txt`)이 머지마다 충돌하기 때문이다.
