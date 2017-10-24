#!/bin/bash
echo "Bienvenido al instalador de CEIC Suite (Versión netinstall)"
echo "Instalando dependencias..."
sudo  apt-get install python3-pip python3-pyqt4 postgresql-9.5 python3-pyqt4 libqt4-dbus libqt4-designer sni-qt -y
sudo  python3 -m pip install -r requirements
echo "¿Tiene la base de datos configurada previamente?[y/n]"
read ans
if [ ans == "n" ]
then
	echo "Creando rol para la base de datos..."
	sudo -u postgres createuser -PE -s ceic_suite
	echo "Creando base de datos..."
	sudo -u postgres createdb -O ceic_suite -E UTF8 ceic_suite
fi
cd ..
echo "Iniciando CEIC suite..."
python3 ceic_suite.py
