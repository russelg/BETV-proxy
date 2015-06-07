# BETV-proxy
Serves as a replacement for a BETV server. (default: pclist.zzfdi.com)

## Setup Instructions

1.  Make sure port 80 is not being used. Follow instructions in the below link for how to do this.

    > http://stackoverflow.com/questions/788348/how-do-i-free-my-port-80-on-localhost-windows

2.  Grab the latest channel XML files for BETV. (I have provided the required XML files already, this is if you want to update them yourself)

    1.  Get Uuid from:

        > http://pclist.yyjbg.com/opsbetv/auth.action?type=1&ack=0000007400010000000000000075

    2.  Use anything to download the XML from the following URL to `chn_response.xml`. A curl example follows.

        ```bash
curl "http://pclist.yyjbg.com/opsbetv/tv.action?type=1&uuid=<Uuid here>" -H "User-Agent: BETV" -o chn_response.xml
        ```

3. Grab the lastest channel XML files for NIJI. (Read #2 note)

    Use anything to download the XML from the following URL to `jp_response.xml`
    ```bash
curl "http://nebox.myniji.tv:7006/xml/tv1/2/tv.xml" -o jp_response.xml
    ```

4. Install python dependencies.

    ```bash
pip install xmltodict bottle requests
    ```

5. Modify your `/etc/hosts` file. (`C:\Windows\System32\drivers\etc\hosts` on Windows)

    ```
    127.0.0.1     pclist.zzfdi.com
    ```

6. Copy the `ppp.conf` from NIJI to BETV. (I have also provided the NIJI `ppp.conf` in this repo)
7. Start the server with:

    ```bash
python betv.py
    ```
