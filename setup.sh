if [ $(id -u) != 0 ]; then
    echo "Please run this script with sudo:"
    echo "sudo $0 $*"
    exit 1
fi

# Creamos el script de inicialización del AP
echo "iw phy phy0 interface add hotspot type __ap
ifconfig hotspot 192.168.10.1 up

tmux new-session -d -s init 'sudo hostapd $(pwd)/config/hostapd.conf'
tmux split-pane -h -t init 'sudo udhcpd -f'" > init.sh

# Para generar el AP (modificar los ficheros udhcpd.conf y hostapd.conf)
apt install -y hostapd
apt install -y udhcpd

cp config/udhcpd.conf /etc/udhcpd.conf

# Creamos el cron para que se ejecute el script cada vez que se inicie el equipo
{ crontab -l; echo "@reboot $(pwd)/init.sh"; } | crontab -

# Suite de aircrack-ng
apt install -y aircrack-ng
# Librerias utilizadas en el código de la herramienta
pip install -r requirements.txt

# Repositrio de la librería python-ardrone
git clone https://github.com/venthur/python-ardrone
cp dron_crontrol.py python-ardrone
