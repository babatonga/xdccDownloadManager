from django.db import models

class IRCConnection(models.Model):
    id = models.AutoField(primary_key=True)
    server = models.CharField(max_length=255, unique=True, db_index=True)
    port = models.IntegerField()
    ssl = models.BooleanField(default=False)
    nickname = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    use_sasl = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    last_scan = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.server
    
class IRCChannel(models.Model):
    id = models.AutoField(primary_key=True)
    channel = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    server = models.ForeignKey(IRCConnection, on_delete=models.CASCADE, related_name='channels')

    def __str__(self):
        return self.channel
    
class XDCCOffer(models.Model):
    id = models.AutoField(primary_key=True)
    channel = models.ForeignKey(IRCChannel, on_delete=models.CASCADE)
    bot = models.CharField(max_length=255)
    pack_number = models.IntegerField()
    pack_name = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pack_name