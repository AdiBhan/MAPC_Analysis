runtest:
	gcc -o test test.c
	./test
runconsole:
	python3 console.py
analysis:
	python3 Analysis.py
utility:
	python3 Utilities.py