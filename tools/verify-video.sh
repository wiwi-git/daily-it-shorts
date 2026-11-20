#!/bin/bash
# 영상 한 편의 "검증 기준"(CLAUDE.md)을 순서대로 실행하고, 하나라도 어기면 멈춘다.
#   사용: tools/verify-video.sh <영상폴더> [--no-render]
#   1. python3 build.py (예제 실행·대조 포함)
#   2. hyperframes check: 오류 0건
#   3. 자막 공백: 대사 중 자막 없는 시간 0초
#   4. snapshot --review: 장면별 프레임 + 휴대폰 폭 시트 (경로를 출력 → 직접 열어 확인)
#   5. 렌더링 → <저장소>/output/<영상폴더>.mp4, ffprobe로 1080×1920 · 오디오 트랙 확인
# 음성(assets/vo/*.mp3)이 없으면 gen_vo.py를 먼저 실행한다.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
[ $# -ge 1 ] || { echo "사용: $0 <영상폴더> [--no-render]"; exit 2; }
name=$(basename "$1")
dir="$root/$name"
[ -f "$dir/build.py" ] || { echo "✗ $dir/build.py 없음"; exit 2; }
HF="npx --yes hyperframes@0.8.214"
cd "$dir"

if ! ls assets/vo/*.mp3 >/dev/null 2>&1; then
  echo "▶ 음성 생성 (assets/vo 비어 있음)"
  "$root/.venv/bin/python" gen_vo.py | tail -1
fi

echo "▶ 1/5 빌드"
python3 build.py | tail -1

echo "▶ 2/5 hyperframes check"
out=$($HF check 2>&1 || true)
errors=$(printf '%s\n' "$out" | grep -Eo '[0-9]+ error\(s\)' | awk '{s+=$1} END {print s+0}')
printf '%s\n' "$out" | grep -E '⚠|✗' | grep -v 'line_unread\|timeline_track_too_dense\|nested_structure_needs_subcomposition' || true
[ "$errors" = 0 ] || { echo "✗ check 오류 $errors건"; printf '%s\n' "$out" | grep -E 'error|✗' | head -20; exit 1; }
echo "✓ check 오류 0건"

echo "▶ 3/5 자막 공백"
python3 - <<'EOF'
import json, re
m = re.search(r"^SPEED = ([\d.]+)|load\(speed=([\d.]+)\)", open("build.py").read(), re.M)
speed = float(m.group(1) or m.group(2)) if m else 1.0
lead, gap_between = round(0.3 / speed, 3), round(0.45 / speed, 3)
html = open("index.html").read()
caps = sorted((float(a), float(a) + float(d)) for a, d in
              re.findall(r'class="clip cap" data-start="([\d.]+)" data-duration="([\d.]+)"', html))
t, gap = lead, 0.0
for s in json.load(open("vo.json")):
    a, b = t, t + s["dur"]
    cur = a
    for x, y in caps:
        if y <= cur or x >= b:
            continue
        if x > cur + 0.01:
            gap += x - cur
        cur = max(cur, y)
    if cur < b - 0.01:
        gap += b - cur
    t = b + gap_between
if gap > 0.02:
    raise SystemExit(f"✗ 대사 중 자막 없는 시간 {gap:.2f}초")
print("✓ 대사 중 자막 없는 시간 0초")
EOF

echo "▶ 4/5 snapshot --review"
snap="$dir/.hyperframes/verify"
$HF snapshot -o "$snap" --review >/dev/null 2>&1
echo "  장면 시트: $(ls "$snap"/review-beats*.jpg 2>/dev/null | head -1)"
echo "  휴대폰 폭: $(ls "$snap"/review-phone*.jpg | tr '\n' ' ')"
echo "  → 위 이미지를 직접 열어 겹침·넘침·가독성을 확인할 것 (자동 판정 아님)"

if [ "${2:-}" = "--no-render" ]; then
  echo "✓ 렌더링 생략 (--no-render)"; exit 0
fi

echo "▶ 5/5 렌더링 + ffprobe"
mp4="$root/output/$name.mp4"
mkdir -p "$root/output"
$HF render -o "$mp4" 2>&1 | tail -1
probe=$(ffprobe -v error -show_entries stream=codec_type,width,height -show_entries format=duration -of csv=p=0 "$mp4")
printf '%s\n' "$probe" | grep -q '^video,1080,1920' || { echo "✗ 해상도가 1080×1920이 아님: $probe"; exit 1; }
printf '%s\n' "$probe" | grep -q '^audio' || { echo "✗ 오디오 트랙 없음"; exit 1; }
dur=$(printf '%s\n' "$probe" | tail -1)
python3 -c "import sys; d=float(sys.argv[1]); sys.exit(0 if d<=180 else 1)" "$dur" || { echo "✗ 길이 ${dur}초 > 3분"; exit 1; }
echo "✓ $mp4 · 1080×1920 · 오디오 있음 · $(python3 -c "import sys; d=float(sys.argv[1]); print(f'{int(d//60)}:{round(d%60):02d}')" "$dur")"
