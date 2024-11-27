----- INITIALIZE -----
NOTES:

1. Login credentials
   username: admin
   password: admin

2. Create ssh key
   git config --global user.email "rpi@example.com" && git config --global user.name "rpi" && ssh-keygen -t ed25519 -C "rpi@example.com" -f ~/.ssh/id_ed25519 -N '' && cat ~/.ssh/id_ed25519.pub

3. Add ssh key to github

4. git clone

5) chmod -R +x . Note: might delete

6) DISABLE SCREEN SLEEP
   sudo nano /etc/lightdm/lightdm.conf

   [Seat:*]
   xserver-command=X -s 0 dpms

7) Initialize
   sudo apt update
   sudo apt upgrade -y

8) Install python libraries

9) If use GPIO - see --- GPIO ---
10) If use tensorflow - see --- TENSORFLOW ---

11) try running app.py

12) utils/autostart

----- GPIO -----

1. pip install pigpio
2. sudo systemctl enable pigpiod
3. sudo systemctl start pigpiod
4. sudo pigpiod

----- TENSORFLOW -----

1. pip install --upgrade pip setuptools wheel
2. sudo apt-get install libhdf5-dev
3. pip install tensorflow

- sudo apt install libssl3=3.0.11-1~deb12u2
