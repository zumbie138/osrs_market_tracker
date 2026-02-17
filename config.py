import os
from dotenv import load_dotenv

class Config:
    load_dotenv()
    OSRS_API_BASE = 'https://prices.runescape.wiki/api/v1/osrs'
    OSRS_USER_AGENT = os.getenv('OSRS_USER_AGENT')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    POLL_SECONDS = int(os.getenv('POLL_SECONDS'))
    DB_PATH = os.getenv('DB_PATH')
    ITEM_LIST = {
        10364: 'Strength amulet (t)',
        29455: 'Teleport anchoring scroll',
        6735 : 'Warrior ring',
        29084: 'Sulphur blades',
        12829: 'Spirit shield',
        20517 : 'Elder chaos top',
        23389 : 'Spiked manacles',
        7378 : "Green d'hide chaps (g)",
        2579 : 'Wizard boots',
        12273 : 'Bandos cloak',
        28334 : "Awakener's orb",
    }
 

# Strength amulet (t) 10364
# Teleport anchoring scroll 29455
# Warrior ring 6735
# Sulphur blades 29084
# Spirit shield 12829
# Elder chaos top 20517
# Spiked manacles 23389
# Green d'hide chaps (g) 7378
# Wizard boots 2579
# Bandos cloak 12273
# Awakener's orb 28334
 
	

# Uncooked egg 7076

# Divine super strength potion(3) 23712
# Turquoise hat 664
# Rune axe 1359
#  Sarachnis cudgel 23528
# Mystic set (blue) 23113
# Black brutal 4788
# Dragon platelegs 4087
# Magic sapling 5374
# Large steel keel parts	32026
# Saradomin brew(4) 6685
# Oathplate shards 30765
# Rune crossbow 9185
# Dragon plateskirt 4585
# Dragon longsword 1305
# Blue d'hide chaps 2493
# Mystic robe top 4091
#Rune platebody 1127
#Amulet of glory(6) 11978
# Divine super combat potion(4) 23685
#Bracelet of ethereum (uncharged) 21817 
# Ring of wealth (5) 11980
# Rune chainbody 1113
#Large ironwood hull parts 32077
#Hunters' sunlight crossbow 28869
#Black scimitar 1327
#Divine bastion potion(2) 24641
#Broken antler 31086
#Bastion potion(3) 22464
#2363 : 'Runite bar',
#8782 : 'Mahogany plank',
#451 : 'Runite ore',
#536 : 'dragon bones',
#12625 : 'stamina potion(4)',
#2434 : 'prayer potion(4)',
#385 : 'shark',
#2361 : 'adamantite bar'
#Dragon scimitar 4587