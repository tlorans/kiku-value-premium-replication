.PHONY: test site preview freeze

test:
	uv run pytest

site:
	uv run quarto render site

preview:
	uv run quarto preview site

freeze:
	rm -rf site/_freeze
	uv run quarto render site
