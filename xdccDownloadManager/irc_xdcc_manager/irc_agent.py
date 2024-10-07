import signal
from .models import IRCConnection, IRCChannel, XDCCOffer
import irc3
from irc3.compat import asyncio
from django.conf import settings
import re
import os
import logging
import threading
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


DOWNLOAD_DIR = os.path.join(settings.BASE_DIR, 'downloads')
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@irc3.plugin
class XDCCToDatabase:
    requires = ['irc3.plugins.core', 'irc3.plugins.ctcp', 'irc3.plugins.dcc', 'irc3.plugins.log']
    
    def __init__(self, bot):
        self.bot = bot
        self.log = logger
        
    def connection_made(self):
        self.log.info(f"connection made to {self.bot.config.host}")

    def server_ready(self):
        self.log.info(f"server ready {self.bot.config.host}")

    def connection_lost(self):
        self.log.info(f"connection lost to {self.bot.config.host}")
    
    # Event triggered when a XDCC offer is received. Returns botname, pack_number, pack_size, pack_name
    # example: <+[MG]-OWN|EU|S|HellBee> #378  432x [6.4G] Ghostbusters.Legacy.AKA.Afterlife.2021.German.AAC.5.1.DL.1080p.BluRay.x264-oWn.mkv 
    @irc3.event((r'''(@(?P<tags>\S+) )?:(?P<mask>\S+) (?P<event>[A-Z]+)'''
                 r''' (?P<target>#\S+)(\s:(?P<data>.*)|$)'''))
    async def on_xdcc_offer(self, mask, event, target=None, data=None, **kwargs):
        if event != 'PRIVMSG' and target and target.is_channel and data:
            match = re.match(r'^<\+(?P<botname>[^>]+)> #(?P<pack_number>\d+)\s+(?P<gets>\d+x)\s+\[(?P<pack_size>[^\]]+)\]\s+(?P<pack_name>.+)$', data)
            if match:
                logger.debug(f"Data {data} matches XDCC offer pattern")
                botname = match.group('botname')
                pack_number = match.group('pack_number')
                pack_gets = match.group('gets')
                pack_size = match.group('pack_size')
                pack_name = match.group('pack_name')
                
                host = self.bot.config.host
                
                existing_offer =  await sync_to_async(XDCCOffer.objects.filter)(channel__server__server=host, bot=botname, pack_number=pack_number, pack_name=pack_name, size=pack_size).first()
                if not existing_offer:
                    channel = await sync_to_async(IRCChannel.objects.get)(server__server=host, channel=target)
                    await sync_to_async(XDCCOffer.objects.create)(channel=channel, bot=botname, pack_number=pack_number, pack_name=pack_name, size=pack_size)
                    self.log.info(f"Offer {pack_name} added to database")
                else:
                    self.log.debug(f"Offer {pack_name} already in database")
            else:
                self.log.debug(f"Data {data} does not match XDCC offer pattern")
                    
    @irc3.event(irc3.rfc.CTCP)
    async def on_ctcp(self, mask=None, **kwargs):
        name, host, port, size = kwargs['ctcp'].split()[2:]
        self.log.info('%s is offering %s', mask.nick, name)
        filepath = os.path.join(DOWNLOAD_DIR, name)
        conn = await self.bot.create_task(self.bot.dcc_get(
            mask, host, port, filepath, int(size)))
        await conn.closed
        self.log.info('file received from %s', mask.nick)
    
    
    @irc3.extend
    def download_xdcc(self, pack_number, target, **kwargs):
        if not target:
            self.log.error("No target specified")
            return
        self.bot.privmsg(target, f"xdcc send #{pack_number}")
        self.log.info(f"Sent XDCC send command for pack {pack_number} to {target}")           
        
        
class XDCCServerListener():
    def __init__(self, server):
        connection = IRCConnection.objects.get(server=server, active=True)
        if not connection:
            raise Exception(f"Connection {server} not found")
        if not connection.channels.filter(active=True).exists():
            raise Exception(f"No active channels found for connection {server}")
        self.thread = None
        self.loop = None
        self.bot = None
        self.should_stop = threading.Event()
        
        self.ssl = connection.ssl
        self.sasl = connection.use_sasl
        self.username = connection.nickname
        self.password = connection.password
        
        self.config = dict(
            nick=connection.nickname,
            username=connection.nickname,
            host=connection.server,
            port=connection.port,
            ssl=connection.ssl,
            includes=[
                'irc3.plugins.core',
                'irc3.plugins.autojoins',
                'irc3.plugins.ctcp',
                'irc3.plugins.dcc',
                'irc3.plugins.log',
                __name__,
            ],
            autojoins=[channel.channel for channel in connection.channels.filter(active=True)],
        )
        
    def __run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.config['loop'] = self.loop
        
        if self.ssl and self.sasl and self.password:
            self.config['sasl_username'] = self.username
            self.config['sasl_password'] = self.password
            
        self.bot = irc3.IrcBot.from_config(self.config)
        self.bot.log = logger
        
        logger.info(f"Starting IRC client for {self.config['host']}")
        self.bot.run(forever=False)
        
        try:
            self.loop.run_until_complete(self.bot.loop.run_forever())
        except Exception as e:
            logger.error(f"Error running IRC client: {e}")
        
    def start(self):
        if self.thread is None or not self.thread.is_alive():
            logger.info("Starting IRC client thread")
            self.thread = threading.Thread(target=self.__run)
            self.thread.start()
                
        
    def stop(self):
        logger.info(f"Stopping IRC client for {self.config['host']}")
        if self.bot:
            try:
                self.bot.quit("Stopping client")
                self.bot.loop.call_soon_threadsafe(self.bot.loop.stop)
                self.bot.loop.call_soon_threadsafe(self.bot.loop.close)
            except Exception as e:
                logger.error(f"Error stopping IRC client: {e}")
        if self.loop:
            try:
                self.loop.call_soon_threadsafe(self.loop.stop)
                self.loop.call_soon_threadsafe(self.loop.close)
            except Exception as e:
                logger.error(f"Error stopping loop: {e}")
        if self.thread:
            self.thread.join(1.0)
            logger.info("Thread joined")
        
    async def download_xdcc(self, pack_number, target):
        await self.bot.download_xdcc(pack_number, target)
        