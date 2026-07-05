.PHONY: install playground generate-traces grade run-gateway

install:
	uv sync

playground:
	uv run adk web ./

generate-traces:
	uv run python tests/eval/generate_traces.py

grade:
	uv run python tests/eval/grade.py

run-gateway:
	uv run uvicorn strawberry_agent.main:app --host 127.0.0.1 --port 8080

