# Dongmin Go — CV & Academic Homepage

CV와 홈페이지를 이 Public 저장소 하나에서 관리합니다.

- 사이트: https://godongdongmin.github.io/
- 공개 CV: [files/Dongmin_Go_CV.pdf](files/Dongmin_Go_CV.pdf)
- 프로필 수정: [source/profile.json](source/profile.json)
- 새 자료를 넣는 곳: [inbox/](inbox/README.md)

## 다른 PC에서 시작하기

```sh
git clone https://github.com/godongdongmin/godongdongmin.github.io.git
cd godongdongmin.github.io
```

필수 환경은 Git, Python 3.9 이상, XeLaTeX입니다. Python 외부 패키지는 필요하지 않습니다.

- **Windows:** Python과 TeX Live를 설치하고 `python --version`, `xelatex --version`이 실행되는지 확인합니다.
- **macOS:** Python 3와 MacTeX를 설치합니다. 아래 명령의 `python`을 `python3`로 바꿔도 됩니다.
- **Ubuntu/Debian:** `sudo apt install python3 texlive-xetex texlive-latex-extra tex-gyre`로 준비할 수 있습니다.

CV는 Times New Roman이 설치되어 있으면 사용하고, 없으면 TeX Gyre Termes를 사용합니다. 후자는 TeX Live/MacTeX의 `tex-gyre` 패키지로 설치할 수 있습니다. 글꼴에 따라 줄바꿈이 달라질 수 있으므로 PDF를 확인합니다. 독점 글꼴 파일은 저장소에 포함하지 않습니다.

## 수정하는 파일

| 파일/폴더 | 용도 |
|---|---|
| `source/profile.json` | 이름·연락처·학력·경력·논문·수상 등 CV/홈페이지 공통 데이터 |
| `source/build.py` | HTML 생성 및 CV LaTeX 레이아웃 |
| `source/research_page.py` | 연구 소개 페이지 내용 |
| `assets/style.css` | 웹사이트 스타일 원본 |
| `assets/portrait.jpg` | 공개 프로필 사진 |
| `assets/myomimetic-poster.jpg` | 공개 영상 포스터 |
| `files/myomimetic-exosuit-video.mp4` | 공개 연구 영상 |
| `inbox/` | 수정에 참고할 자료를 넣는 로컬 작업 공간 |
| `_build/`, `output/` | 생성된 중간 파일과 배포 ZIP; Git에서 제외 |

사진·영상은 위 경로에 한 벌만 관리합니다. `index.html`, `research/myomimetic-exosuit/index.html`, `files/Dongmin_Go_CV.pdf`는 생성 결과이므로 내용 수정은 원본 데이터/스크립트에서 합니다.

## 자료를 넣고 반영하기

1. 새 자료를 `inbox/awards`, `education`, `photos`, `research`, `references`, `notes` 중 알맞은 폴더에 넣습니다.
2. 자료에서 **공개할 내용만** 골라 `source/profile.json` 등에 반영합니다. 자료를 넣는 것만으로 내용이 자동 변환되지는 않습니다. 편집 도구나 작업자에게 해당 경로와 반영할 내용을 알려주세요.
3. 사진·영상을 공개하려는 경우에만 `assets/` 또는 `files/`의 운영 파일을 교체합니다.

`inbox/`의 폴더 구조와 안내문만 Git에 포함됩니다. **그 안에 넣은 파일은 커밋·푸시·배포 ZIP에 포함되지 않으며 다른 PC로 자동 동기화되지 않습니다.** `.gitignore`는 암호화 기능이 아니므로 비공개 자료에 `git add -f`를 사용하지 않습니다. 필요한 원본 자료는 별도 비공개 전달 수단으로 옮깁니다. 공개 저장소의 `source/profile.json`에는 개인 검토 메모, 인증 정보, 미공개 원고를 넣지 않습니다.

## 빌드·확인·배포

저장소 루트에서 실행합니다.

```sh
git pull --ff-only
# source/profile.json 등 수정
python source/build.py
python source/check.py
```

생성되는 파일은 다음과 같습니다.

- `files/Dongmin_Go_CV.pdf`: Git에 포함되는 최신 CV
- `output/Dongmin_Go_CV.pdf`: 같은 PDF의 로컬 출력 사본
- `_build/Dongmin_Go_CV.tex`: 생성된 LaTeX 원본
- `output/godongdongmin.github.io.zip`: 공개 사이트 파일만 포함한 배포용 ZIP

HTML만 수정하고 기존 PDF를 유지하려면 `python source/build.py --site-only`를 사용합니다. 이 옵션에는 XeLaTeX가 필요하지 않습니다.

생성된 PDF와 `index.html`을 확인한 다음:

```sh
git status --short
git diff
git add source assets files index.html research README.md AGENTS.md .gitignore .gitattributes inbox
git diff --cached --stat
git commit -m "Update CV and homepage"
git push origin main
```

`inbox/` 내부 자료는 위 명령에도 무시됩니다. 첫 push 전 GitHub 인증과 본인의 Git 이름·이메일 설정이 필요할 수 있습니다. 기존 Pages 설정인 `main` / `/(root)`로 배포되며 별도의 저장소, 토큰 파일, 자동 커밋 워크플로는 필요하지 않습니다.

공개 배포 후에는 `python source/check_live.py`로 현재 사이트와 CV의 일치 여부를 확인할 수 있습니다. 선택적인 브라우저 검증은 Node.js 22 이상과 Chrome/Chromium을 준비하고 `node source/check_layout.mjs`를 실행합니다. 자동 탐지가 안 되면 `CHROME_PATH` 환경변수에 실행 파일 경로를 지정합니다.

## 공개 파일 범위

이 저장소에 커밋된 파일은 모두 공개됩니다. PDF/영상 외에 편집 데이터와 생성 코드도 공개 대상입니다. Pages는 현재 저장소 루트에서 서비스하므로 소스 파일도 URL로 접근 가능할 수 있습니다. 공개하지 않을 자료는 `inbox/` 안에 두고, 배포 ZIP은 빌더가 지정한 공개 파일만 포함합니다.

논문 원고는 현재 배포하지 않습니다. 준비 중 논문의 서지·제출 전 상태 및 공개 영상만 유지합니다.
