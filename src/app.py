import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from composer import conf
from factory.standard_discord_bot_factory import StandardDiscordBotFactory
from runner.standard_discord_bot_runner import StandardDiscordBotRunner


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')

    def log_message(self, format, *args):
        return


def start_health_check_server() -> None:
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logging.info(f'HTTP server started on port {port}')


class App:
    '''Entry point of the program.'''

    def start(self) -> None:
        '''Starts the program.'''

        start_health_check_server()

        fac = StandardDiscordBotFactory(conf)
        StandardDiscordBotRunner(conf, fac).run()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s,%(levelname)s,%(message)s',
        datefmt='%d/%m/%Y %H:%M:%S'
    )

    App().start()
