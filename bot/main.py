from urllib import request
import urllib.parse
import discord
import os
import sys
import random
print("    $   $  RUNNING")
sys.stdout.flush()
USER_AGENTS = ["Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1","Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/107.0.5304.66 Mobile/15E148 Safari/604.1","Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/106.0 Mobile/15E148 Safari/605.1.15"]

def download_and_decode_html(url):
    websiteurl = "https://sci-hub.se/" + url
    req = request.Request(url=websiteurl, headers={'User-Agent' : USER_AGENTS[random.randrange(3)]})
    fp = request.urlopen(req)
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()
    print("decoded...")
    sys.stdout.flush()
    return mystr

def download_file(url):
    '''queries sci-hub and then downloads pdf and names it its corresponding DOI
    returns the DOI
    inputs: url to download
    output: tuple of: file object representing the pdf just downloaded from sci-hub, and its associated DOI
    '''
    #open sci-hub and try and get the whole page to later extract download link
    mystr = download_and_decode_html(url)
    #extract the url. the conditional is because sometimes it's self-hosted, sometimes it's not
    #the try block is incase there is %2F
    try:
        print("block1")
        downloadurl = mystr[mystr.index("location.href=") + 16 :mystr.index("?download=true")+14]
        
    except:
        try:
            print("block2")
            url = urllib.parse.unquote(url)
            print(url)
            mystr = download_and_decode_html(url)
            downloadurl = mystr[mystr.index("location.href=") + 16 :mystr.index("?download=true")+14]
        except:
            print("block3")
            url = url.replace("%2F","/")
            url = url.replace("%2f","/")
            mystr = download_and_decode_html(url)
            downloadurl = mystr[mystr.index("location.href=") + 16 :mystr.index("?download=true")+14]
    if downloadurl[0] == "/":
        downloadurl = "https://" + downloadurl[1:]
    else:
        downloadurl = "https://sci-hub.se/" + downloadurl
    sys.stdout.flush()
    print("   downloadurl" + downloadurl)
    sys.stdout.flush()

    #get doi
    doi_index = mystr.index('<div id = "doi">') + 16
    doi = ""
    for i in mystr[doi_index:]:
        if i == "<":
            break
        doi += i
    doi = doi.strip()
    print("  doi" + doi)
    sys.stdout.flush()

    #delete illegal filename characters
    filename = list(doi)
    for i in range(len(filename)):
        if filename[i] == "/":
            filename[i] = "-"
        if filename[i] == ":":
            filename[i] = ";"
    #make filename not retarded
    filename = ''.join([str(item) for item in filename]) + ".pdf"
    print("   $" + filename + "$")
    sys.stdout.flush()
    print("   $" + downloadurl + "$")
    sys.stdout.flush()
    #download and return
    opener = request.build_opener()
    opener.addheaders = [('User-Agent',USER_AGENTS[random.randrange(3)])]
    request.install_opener(opener)
    return request.urlretrieve(downloadurl, filename)[0],doi



#makes sure url has valid protocol in front
def url_conform(url):
    con_url = url
    con_url = con_url.strip()
    if con_url[:7] != "http://":
        if con_url[:8] == "https://":
            return con_url
        colindex = 11
        try:
            #this makes sure it doesn't overwrite some other protocol. if :// appears before 10, it's likely just some weird protocol. if not, assume and hope it's http
            colindex = con_url.index("://")
        except: 
            print(":// not found. assuming http://")
            sys.stdout.flush()
        if colindex > 10:
            con_url = "http://" + con_url
    return con_url

## ## ## ##
## ## ## ##
## ## ## ##

#discord stuff
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    sys.stdout.flush()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$sh '):
        print("recieved message: " + message.content)
        sys.stdout.flush()
        await message.add_reaction("👍")
        url = url_conform(message.content[4:])
        try:
            contents = download_file(url)
            filename = contents[0]
            with open(filename, 'rb') as fp:
                await message.channel.send(file=discord.File(fp, contents[1] + ".pdf"))
                print("sent file")
                sys.stdout.flush()
            if os.path.exists(filename):
                print("attempted to remove file" + filename)
                sys.stdout.flush()
                os.remove(filename)
                print("current pwd contents: " + str(os.listdir()))
                sys.stdout.flush()
            else:
                 print("tried to remove " + filename +" but not found")
                 sys.stdout.flush()
        except Exception as e:
            print(e)
            sys.stdout.flush()
            print("general error")
            sys.stdout.flush()
            await message.channel.send("there was an error :(. malformed message or paper not found on sci-hub.se. if it is, dm the link to @buck#9576 so I can fix the bot :)")

    if message.content.startswith('$help'):
        await message.channel.send("usage: `$sh urlofpaper`")
      
if __name__ == '__main__':
    client.run(os.getenv('DISCORD_TOKEN'))
        

