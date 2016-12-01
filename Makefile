default: chromecredentials.py
	pip install virtualenv
	virtualenv venv
	$(source venv/bin/activate)
	pip install -r requirements.txt
	python chromecredentials.py
	deactivate
