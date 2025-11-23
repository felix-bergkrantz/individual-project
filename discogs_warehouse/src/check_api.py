from discogs_client import Client
from env import DISCOGS_TOKEN

d = Client("discogs-warehouse/1.0", user_token=DISCOGS_TOKEN)
me = d.identity()
print("Discogs API OK. User:", me.username)