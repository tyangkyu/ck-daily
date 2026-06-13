# ck-daily

`ck-daily`는 주요 AI, 클라우드, 플랫폼, 디지털 커머스 신호를 수집해 경영진용 데일리 브리프를 생성하는 Python 파이프라인입니다. RSS 수집, 정제, 신호 점수화, 인사이트 생성, Markdown/DOCX/PDF 렌더링, Slack 배포 결과 기록을 포함합니다.

## 설치

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## 환경변수

```bash
cp .env.example .env
```

| 이름 | 필수 | 설명 |
|---|---:|---|
| `SLACK_BOT_TOKEN` | Slack 전송 시 | `report.pdf`를 Slack 파일로 업로드할 Bot token |
| `SLACK_CHANNEL_ID` | Slack 전송 시 | 게시 대상 Slack 채널 ID |
| `RUN_MODE` | 아니오 | 기본값 `draft`; 운영 전송은 CLI의 `--mode send` 사용 |

민감 정보는 `.env` 또는 실행 환경에만 넣고 GitHub에 올리지 않습니다. Slack token, API key, OAuth secret, DB 접속 정보는 README, 로그, 테스트 fixture에 남기지 마세요.

## 실행

전체 파이프라인 dry-run:

```bash
python3 scripts/daily_pipeline.py --date 2026-05-31 --dry-run
```

Slack에 실제 게시:

```bash
python3 scripts/daily_pipeline.py --date 2026-05-31 --mode send
```

라이브 Slack 전송은 `SLACK_BOT_TOKEN`과 `SLACK_CHANNEL_ID`가 필요합니다. 토큰이 없으면 보고서 생성과 검증은 완료되지만, Slack 전송 결과는 `blocked_missing_slack_token`으로 기록됩니다. 봇이 대상 채널에 없으면 `blocked_bot_not_in_channel`으로 기록됩니다. 전송 성공 기준은 Slack 메시지 게시뿐 아니라 `report.pdf` 파일 첨부 성공까지 포함합니다.

## 단계별 실행

```bash
python3 scripts/init_run.py --date 2026-05-31 --dry-run
python3 scripts/collect_sources.py --run-context Reports/2026-05-31/run-context.json
python3 scripts/clean_and_rank_sources.py --run-context Reports/2026-05-31/run-context.json
python3 scripts/score_signals.py --run-context Reports/2026-05-31/run-context.json
python3 scripts/generate_insights.py --run-context Reports/2026-05-31/run-context.json
python3 scripts/generate_hero_visual.py --run-context Reports/2026-05-31/run-context.json
python3 scripts/render_report.py --run-context Reports/2026-05-31/run-context.json
python3 scripts/render_slack_message.py --run-context Reports/2026-05-31/run-context.json
python3 scripts/send_slack.py --run-context Reports/2026-05-31/run-context.json
python3 scripts/validate_outputs.py --run-context Reports/2026-05-31/run-context.json
```

## 테스트

```bash
pytest
```

## 보안 및 산출물 관리

- `.env`, `.venv`, `.pytest_cache`, `Reports/<date>/`, 로그, OS 임시 파일은 `.gitignore`로 제외합니다.
- `Reports/.gitkeep`만 저장소에 유지하고, 일별 보고서 산출물은 커밋하지 않습니다.
- Slack 커넥터만으로는 로컬 PDF 첨부가 불가능합니다. PDF 첨부가 필요한 운영 게시에는 Slack Bot token 기반 SDK 경로를 사용하세요.
- `blocked_missing_slack_token` 상태가 반복되면 `.env`에 Slack Bot credential을 추가해야 합니다.
- `blocked_bot_not_in_channel` 상태가 반복되면 Slack에서 대상 채널에 Bot/App을 초대해야 합니다.
