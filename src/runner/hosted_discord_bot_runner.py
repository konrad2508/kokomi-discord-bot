import atexit
import http.server
import logging
import subprocess
import time
import threading
import urllib

from runner.standard_discord_bot_runner import StandardDiscordBotRunner


class HostedDiscordBotRunner(StandardDiscordBotRunner):
    '''Extended StandardDiscordBotRunner, additionaly runs a webserver for hosted environments.'''

    def run(self):
        class Webserver(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'OK')

            def log_message(self, format, *args):
                return


        def start_server():
            logging.info(f'starting webserver on port {self.cfg.webserver_port}')

            http.server.HTTPServer(('0.0.0.0', self.cfg.webserver_port), Webserver).serve_forever()

        def start_ping():
            logging.info(f'starting pinging {self.cfg.webserver_url}')

            while True:
                time.sleep(300)

                try:
                    with urllib.request.urlopen(urllib.request.Request(
                        self.cfg.webserver_url,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )) as r:
                        logging.info(f'successfully pinged {self.cfg.webserver_url}')

                except Exception as e:
                    logging.error(f'error pinging {self.cfg.webserver_url}: {e}')

        def start_pot():
            logging.info('starting pot provider')

            sp = subprocess.Popen(
                ['node', '../pot/server/build/main.js', '--port', '4416'],
                # stdout=subprocess.DEVNULL,
                # stderr=subprocess.DEVNULL
            )
            time.sleep(3)

            atexit.register(sp.terminate)


        start_pot()
        threading.Thread(target=start_server, daemon=True).start()
        threading.Thread(target=start_ping, daemon=True).start()

        super().run()
