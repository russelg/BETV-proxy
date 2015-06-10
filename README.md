# BETV-proxy
Serves as a replacement for a BETV server. (default: pclist.zzfdi.com)

## Setup Instructions

1.  Make sure port 80 is not being used. Follow instructions in the below link for how to do this.

    > http://stackoverflow.com/questions/788348/how-do-i-free-my-port-80-on-localhost-windows


2. Install python dependencies.

    ```bash
    pip install xmltodict bottle requests
    ```

3. Modify your `/etc/hosts` file. (`C:\Windows\System32\drivers\etc\hosts` on Windows)

    ```
    127.0.0.1     pclist.zzfdi.com
    ```

4. Copy the `ppp.conf` from NIJI to BETV. (I have also provided the NIJI `ppp.conf` in this repo)

5.  Grab the latest channel XML files for BETV. (I have provided the required XML files already, this is if you want to update them yourself)

    ```bash
    python betv.py update
    ```

6. Start the server with:

    ```bash
    python betv.py
    ```