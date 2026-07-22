.PHONY: pdf clean

pdf:
	latexmk -pdf main.tex

clean:
	latexmk -C main.tex
	rm -f main.bbl main.blg main.run.xml main.synctex.gz
