.PHONY: figures test site preview

figures:
	uv run python figures/make_figures.py

test:
	uv run pytest

site:
	uv run quarto render site

preview:
	uv run quarto preview site
