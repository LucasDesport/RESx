VDT = VDT/newlucas.vdt
RESX = python resx/console.py
%RESX = resx



default:  check


all: clean init parents children  neighbours path sector 


children: ;  $(RESX) children ELCNUC 
parents: ;  $(RESX) parents ELCNUC 

neighbours: ; $(RESX) neighbours --up=1 --down=1  INMFUEL   OILHFO GASRFG

full:; $(RESX) full

path:; $(RESX) path ELCNUC INMFUEL  

readme:; pandoc -o README.html  README.md

check:
	$(RESX) neighbours --up=2 --down=2 INMFUEL
help:
	$(RESX) --help
	
clean:; rm -f *.xml *.lock *.graphml

init:; $(RESX) init VDT/newlucas.vdt

sector:; $(RESX) sector BIO
