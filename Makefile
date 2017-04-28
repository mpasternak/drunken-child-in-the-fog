clean:
	find . -name __pycache__ -print0 -type d | xargs -0 rm -rfv 
	find . -name \*~ -print0 | xargs -0 rm -fv 
	find . -name \*pyc -print0 | xargs -0 rm -fv 
	find . -name \*\\.log -print0 | xargs -0 rm -fv 
	rm -rf .tox

