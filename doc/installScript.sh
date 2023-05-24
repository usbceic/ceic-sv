#!/bin/bash
echo "Bienvenido al instalador de CEIC Suite (Versión netinstall)"
echo "Instalando dependencias..."
sudo apt-get install python3-pip python3-pyqt5 postgresql-9.5 libqt5dbus5 libqt5designer5 qt5-style-plugins -y
sudo  python3 -m pip install -r requirements
echo "¿Tiene la base de datos configurada previamente?[y/n]"
read ans
if [ "$ans" == "n" ]
then
    echo "Verificando si el rol y la base de datos ya existen..."
    if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='ceic_suite'" | grep -q 1 &&
       ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='ceic_suite'" | grep -q 1; then
        echo "Creando rol para la base de datos..."
        sudo -u postgres createuser -PE -s ceic_suite
        echo "Creando base de datos..."
        sudo -u postgres createdb -O ceic_suite -E UTF8 ceic_suite
    else
        echo "El rol y la base de datos ya existen."
    fi
fi
cd ..
echo "Iniciando CEIC suite..."
python3 ceic_suite.py
