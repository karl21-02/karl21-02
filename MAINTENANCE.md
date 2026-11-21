# 프로필 관리

프로필 소개는 `profile.json`, 화면 배치는 `README.md`에서 수정합니다.
소개 문구를 수정하면 GitHub Actions가 `info-card.svg`를 다시 생성합니다.

잔디와 활동 통계는 GitHub에 공개되는 프로필 캘린더를 사용합니다.
매일 한국 시간 15:17에 갱신을 요청하며, GitHub 사정에 따라 실행이 늦어질 수 있습니다.
Actions의 **Update profile art → Run workflow**로 수동 실행할 수도 있습니다.
별도의 개인 토큰이나 외부 통계 서비스는 사용하지 않습니다.

## 로컬 실행

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/fetch_contributions.py
.venv/bin/python scripts/render_heatmap_svg.py
.venv/bin/python scripts/make_info_card.py
```

## 사진 변경

`assets/avatar.png`를 원하는 사진으로 교체한 뒤 아래 명령을 실행합니다.
사진 전처리는 로컬에서만 실행하며, 매일 실행되는 워크플로에는 이미지 모델이 필요 없습니다.

```sh
.venv/bin/python -m pip install -r scripts/portrait-requirements.txt
.venv/bin/python scripts/prep_photo.py
.venv/bin/python scripts/make_ascii_svg.py
```

`assets/source-prepped.png`와 `karl-ascii.svg`도 함께 커밋합니다.
애니메이션은 한 번 재생한 뒤 멈추며, 기기의 동작 줄이기 설정에서는 정지 화면을 표시합니다.

원본 디자인 가이드: [Avi Vashishta](https://www.avivashishta.com/blog/build-animated-github-profile-readme).
