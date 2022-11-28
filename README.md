# Entrega final

El alumno deberá entregar una breve presentación que será expuesta en clase sobre el funcionamiento de la herramienta. No se deberá profundizar en los problemas, fases o cualquier otro aspecto de la herramienta más allá de para que sirve y como funciona. Se recomienda que sea desarrollada una demostración de la herramienta desarrollada para verificar su funcionamiento.

La presentación debería tener una duración aproximada de 5-10 minutos, no debiendo superar en ningún caso los 15 minutos.

En la presente entrega deberá proporcionarse tanto la presentación como el código que será directamente subido al GitHub de Proyectos IV (https://github.com/HackingUtad/ProyectosIV/). Se proporcionará acceso a los alumnos a dicho repositorio para que puedan hacer pruebas con las herramientas, de cara a poder utilizarlas en el 2º cuatrimestre, así como ampliarlas en caso de continuar con su desarrollo.

---

- [ ]  script volar
- [ ]  incorporar script volar
- [ ]  quitar la reproducción del video
- [ ]  video terminal móvil ejecutando el programa
- [ ]  video general de todo

Esta herramienta está diseñada para tomar control de un dron “Parrot ARDrone 2.0” sin autorización de usuario legítimo. El software le quita el control al piloto y toma el control, permitiendo manejar el dron sin que el usuario pueda volver a tomar control de este. Todo el proceso se realiza de forma automática ejecutando únicamente un script.

## Material necesario

- RaspberryPi 4B
- Tarjeta de red (se ha utilizado la “Alfa AWUS036AC”)
- Dron Parrot ARDrone2.0 para simular a la víctima.

## Software utilizado

- La suite de `aircrack-ng`.
    
    Utilizada para analizar la red en busca del punto de acceso del dron y el usuario para su posterior des autenticación y suplantación.
    
- La librería https://github.com/venthur/python-ardrone para el manejo del dron desde la terminal.

## Instalación

---

Para el AP:

```bash
sudo apt install -y udhcpd hostapd
```

Para la herramienta:

```bash
# Suite de aircrack-ng
sudo apt install -y aircrack-ng

# Librerias utilizadas en el código de la herramienta
pip install -r requirements.txt
# Repositrio de la librería python-ardrone
git clone https://github.com/venthur/python-ardrone
```

## Uso

---

Antes de ejecutar el script tienes que conocer el nombre que tiene la interfaz que vas a utilizar tanto cuando esta en modo monitor como cuando no lo está.

```bash
sudo python3 drone_crack.py <interfaz> [-i <interfaz_mon>]

# if interface == interface_mon
sudo python3 drone_crack.py <interfaz>

# if interface != interface_mon
sudo python3 drone_crack.py <interfaz> -i <interfaz_mon>
```

## Funcionalidades del proyecto

---

Se ha configurado una Raspberry Pi para que cuando se encienda levante un punto de acceso Wifi, convirtiendo la herramienta en portátil, permitiendo controlarla de forma remota y así se pueda acercar más a su objetivo principal, estar montado todo en un dron y así poder afectar a otros drones que se encuentren cerca.

Para ello se ha desarrollado este script el cual tiene que estar como cron para cuando se encienda el dispositivo.

```bash
# Se crea una interfaz virtual para el punto de acceso
iw phy phy0 interface add hotspot type __ap
ifconfig hotspot 192.168.10.1 up

# Se utiliza tmux para que se quede corriendo en segundo plano y se pueda acceder
# desde otra sesión.
tmux new-session -d -s init 'sudo hostapd /home/pi/hostapd.conf'
tmux split-pane -h -t init 'sudo udhcpd -f'

# Para esto se hace uso de los ficheros "udhcpd.conf" ubicado en /etc/
# y el fichero "hostapd.conf" que lo hemos dejado en el directorio /home/pi/drone.
```

![Sesión de tmux para el AP](img/Untitled.png)

Sesión de tmux para el AP

Y la herramienta desarrollada, la cual permite quitarle el control del dron al usuario legítimo de una forma automática. La herramienta ha sido desarrolla en su totalidad con `python3` y llamadas al sistema.

Próximos desarrollos:

- Redirección de trafico del dron a la Raspberry para controlarlo desde el móvil, para un mejor manejo de la nave. (Este desarrollo no se ha realizado ya que se necesitaba tener un dispositivo móvil “rooteado” para poder suplantar la MAC de la víctima).

---

El funcionamiento de la herramienta es el siguiente:

![Flujo de la aplicación](img/Untitled%201.png)

Flujo de la aplicación

- Análisis de la red en busca de un punto de acceso que pertenezca a un dron (filtrando por su MAC).

- Una vez se encuentra el dispositivo se analiza para identificar al usuario que está conectado.

- Cuando se localiza al usuario legítimo se guarda su MAC para suplantarle y se inicia un proceso de desautenticación.

- Una vez se le desautentica se cambia la MAC de la tarjeta de red por la del cliente legítimo.
    
    Este paso es necesario si el dron está volando, ya que una vez se inicia el vuelo, la nave solo puede ser manejada desde el dispositivo que lo inició.
    
- Una vez se impersona la MAC y se desautentica al usuario, se conecta al punto de acceso generado por el drone.

- Una vez se ha conectado ya se puede tomar control de la nave. El software está hecho para que la nave realice unas instrucciones previamente asignadas.
    
    Para esta funcionalidad se ha utilizado la librería `python-ar-drone`. Esta librería está escrita en python2.7, la cual permite controlar todas las funcionalidades del dron desde funciones desarrolladas en python.
    

## PROBLEMAS

---