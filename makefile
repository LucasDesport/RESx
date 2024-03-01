VDT = VDT/newlucas.vdt

CHECK_RESX = python resx/console.py

default:  check




children: ;  @gshow children ELCNUC 
parents: ;  @gshow parents ELCNUC 

neighbours: ; @gshow neighbours INMFUEL 2 2

full:; @gshow full

path:; @gshow path ELCNUC INMFUEL  

readme:; pandoc -o README.html  README.md

check:
	resx neighbours --up=2 --down=2 OILHFO GASRFG
help:
	resx --help
	
clean:; rm -f *.xml *.lock *.graphml
