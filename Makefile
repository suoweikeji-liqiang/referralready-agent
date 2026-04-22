.PHONY: demo test mcp mcp-http

demo:
	python scripts/run_local_demo.py --patient SYN-CKD-001 --specialty nephrology

test:
	pytest -q

mcp:
	python -m app.mcp_server

mcp-http:
	python -m app.mcp_server --transport streamable-http --host 0.0.0.0 --port 8000 --stateless-http
