.PHONY: figures test

figures:
	uv run python figures/make_figures.py

test:
	uv run pytest
