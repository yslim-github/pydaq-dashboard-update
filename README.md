# PyDAQ Dashboard (PySide6 기반 NI-DAQ 실시간 대시보드)

## 프로젝트 개요
- National Instruments( NI ) DAQ 하드웨어를 위한 실시간/오프라인 신호 처리 및 시각화 대시보드
- Python(PySide6, pyqtgraph) 기반 고성능 데스크톱 앱
- 계측/실험/품질 엔지니어를 위한 실무용 솔루션

## 주요 기능
- 실시간 DAQ 데이터 수집/플로팅 (pyqtgraph, QThread)
- 오프라인 데이터 저장/불러오기 (CSV/HDF5)
- 오프라인 재생/일시정지/배속/슬라이더
- 신호 처리(FFT, FIR/IIR 필터, 통계, 플러그인)
- 대시보드 위젯 드래그&드롭, 레이아웃 저장/불러오기
- 다국어(한/영), 테마/컬러맵 설정
- 자동 업데이트 체크, 관리자 권한 프롬프트

## 설치 및 환경설정
1. **Python 3.10+** 설치
2. **NI-DAQmx 드라이버**(21 이상) 설치 (https://www.ni.com/ko-kr/support/downloads/drivers/download.ni-daq-mx.html)
3. **가상환경(uv/venv) 생성 및 패키지 설치**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
4. **환경 파일**
   - requirements.txt, pyproject.toml, .python-version 등 관리

## 실행 방법
```bash
python main.py
```
- NI-DAQ 하드웨어가 연결되어 있지 않으면 가상 데이터/모킹으로 테스트 가능
- 관리자 권한 필요 시 UAC 프롬프트 자동 표시

## 테스트 방법
```bash
python -m unittest discover -s tests -p "*_test.py" -v
```
- 모든 주요 기능에 대해 가상 데이터/모킹 기반 테스트 자동화

## 주요 파일 구조
```
src/
  main.py                # 메인 실행 파일
  daq_worker.py          # DAQ QThread 데이터 수집
  plot_widget.py         # 실시간 플롯 위젯
  daq_config_widget.py   # DAQ 설정 위젯
  data_io.py             # 데이터 저장/불러오기
  offline_player.py      # 오프라인 재생 컨트롤러
  signal_pipeline.py     # 신호 처리/플러그인
  dashboard.py           # 대시보드 위젯
  settings_widget.py     # 다국어/테마/컬러맵 설정
  admin_utils.py         # 관리자 권한 확인/UAC
  update_checker.py      # 자동 업데이트 체크
```

## NI-DAQmx 안내
- 실제 하드웨어 사용 시 NI-DAQmx 드라이버 필수
- 테스트/개발 시에는 가상 데이터/모킹으로 동작 확인 가능

## 배포/업데이트/코드 서명 안내
- 실제 배포 시 PyInstaller 등으로 exe 패키징 권장
- 자동 업데이트 체크 URL/서버는 실제 운영 환경에 맞게 수정 필요
- 보안 강화를 위해 코드 서명(Windows: signtool 등) 적용 권장

## 문의/기여
- 이 저장소는 실무/연구/교육 목적 모두 환영
- 이슈/기여/문의는 GitHub Issue 또는 PR로 남겨주세요. 