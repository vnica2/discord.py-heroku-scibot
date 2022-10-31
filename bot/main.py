from urllib import request
import discord
import os

#queries sci-hub and then downloads pdf and names it its corresponding DOI
def download_file(url):    
    websiteurl = "https://sci-hub.se/" + url
    fp = request.urlopen(websiteurl)
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()

    downloadurl = mystr[mystr.index("location.href=") + 16 :mystr.index("?download=true")+14]
    if downloadurl[0] == "/":
        downloadurl = "https://" + downloadurl[1:]
    else:
        downloadurl = "https://sci-hub.se/d" + downloadurl
    print("   mystr" + mystr)
    print("   downloadurl" + downloadurl)

    doi_index = mystr.index('<div id = "doi">') + 16
    doi = ""
    for i in mystr[doi_index:]:
        if i == "<":
            break
        doi += i
    doi = doi.strip()
    print("  doi" + doi)
    #upload, then delete after done

    filename = list(doi)
    for i in range(len(filename)):
        if filename[i] == "/":
            filename[i] = "-"
        if filename[i] == ":":
            filename[i] = ";"
    filename = ''.join([str(item) for item in filename]) + ".pdf"
    print("   $" + filename + "$")
    print("   $" + downloadurl + "$")
    return request.urlretrieve(downloadurl, filename)[0],doi
#makes sure url has https:// in front
def url_conform(url):
    con_url = url
    con_url = con_url.strip()
    if con_url[:8] != "https://":
        con_url = "https://" + con_url
    return con_url

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$sh '):
        print("recieved message: " + message.content)
        url = url_conform(message.content[4:])
        try:
            contents = download_file(url)
            filename = contents[0]
            with open(filename, 'rb') as fp:
                await message.channel.send(file=discord.File(fp, contents[1] + ".pdf"))
                print("sent file")
            if os.path.exists(filename):
                print("attempted to remove file" + filename)
                os.remove(filename)
            else:
                 print("tried to remove " + filename +" but not found")
        except Exception as e:
            print(e)
            print("general error")
            await message.channel.send("there was an error :(. malformed message or paper not found on sci-hub.se. if it is, dm the link to @buck#9576 so I can fix the bot :)")

    if message.content.startswith('$help'):
        await message.channel.send("usage: `$sh urlofpaper`")

client.run('MTAzNjQ0ODk2MjkzNDIzMTE0MQ.Gf_duX.nZ10GwDzIASaxAbrQ3zsSWrHauiZNsseTEO6uw')
