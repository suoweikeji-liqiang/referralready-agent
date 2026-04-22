.PHONY: demo test mcp

demo:
	python scripts/run_local_demo.py --patient SYN-CKD-001 --specialty nephrology

test:
	pytest -q

mcp:
	python -m app.mcp_server
