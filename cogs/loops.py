import json, http3, discord
import aiohttp
from discord.ext import commands, tasks
from discord.utils import get

HTTP = http3.AsyncClient()


class Loops(commands.Cog):
    def __init__(self, client):
        print("[Cog] Loops has been initiated")
        self.client = client
        self.BanListCache = []

    @commands.command()
    @commands.is_owner()
    async def startloop(self, ctx):
        response = await ctx.reply("Ban checker has been started.")
        await response.delete(delay=5)
        await ctx.message.delete(delay=5)
        await self.banchecker.start()

    @commands.command()
    @commands.is_owner()
    async def stoploop(self, ctx):
        response = await ctx.reply("Ban checker has been stopped.")
        await response.delete(delay=5)
        await ctx.message.delete(delay=5)
        self.banchecker.stop()

    @tasks.loop(seconds=30)
    async def banchecker(self):
        with open("config.json", "r") as f:
            config = json.load(f)
        banList = await self.getbanlist()
        banList = await self.processlist(banList)
        banList = await self.compareList(banList)
        # The Embed
        channel = self.client.get_channel(config["bans_channel"])
        for i in banList:
            embedVar = discord.Embed(
                title=f"{config['organization_name']}", color=0x00FF00
            )
            embedVar.add_field(
                name="Player Information",
                value=f"{banList[i]['playername']} - {banList[i]['steamid']}",
                inline=False,
            )
            embedVar.add_field(
                name="Ban Information",
                value=f"Ban Length: {banList[i]['timestamp']} - Expires: {banList[i]['expires']} \n `{banList[i]['reason']}`",
                inline=False,
            )
            embedVar.add_field(
                name="Links",
                value=f"Profile: [{banList[i]['steamid']}]({banList[i]['profileurl']})",
                inline=False,
            )
            embedVar.set_thumbnail(url=banList[i]["avatar"])
            embedVar.set_footer(text="Created by Gnomeslayer#5551")
            await channel.send(embed=embedVar)

    async def getbanlist(self):
        with open("config.json", "r") as f:
            config = json.load(f)
        bmtoken = f'Bearer {config["battlemetrics_token"]}'
        url = f"https://api.battlemetrics.com/bans?filter[organization]={config['organization_id']}&include=user,server&page[size]={config['pagesize']}"
        response = ""
        async with aiohttp.ClientSession(headers={"Authorization": bmtoken}) as session:
            async with session.get(url=url) as r:
                response = await r.json()
        data = response
        with open("bandata.json", "w") as f:
            f.write(json.dumps(data, indent=4))

        return data

    async def processlist(self, banlist):
        newList = {}
        admins = {}
        for i in banlist["included"]:
            if i["type"] == "user":
                admins[i["attributes"]["id"]] = i["attributes"]["nickname"]

        for i in banlist["data"]:
            if i["type"] == "ban":
                if i["relationships"].get("user"):
                    newList[i["id"]] = {
                        "banid": i["id"],
                        "playername": i["meta"]["player"],
                        "timestamp": i["attributes"]["timestamp"],
                        "expires": i["attributes"]["expires"],
                        "reason": i["attributes"]["reason"],
                        "note": i["attributes"]["note"],
                        "bmid": i["attributes"]["identifiers"][0]["id"],
                        "steamid": i["attributes"]["identifiers"][0]["metadata"][
                            "profile"
                        ]["steamid"],
                        "avatar": i["attributes"]["identifiers"][0]["metadata"][
                            "profile"
                        ]["avatarfull"],
                        "profileurl": i["attributes"]["identifiers"][0]["metadata"][
                            "profile"
                        ]["profileurl"],
                        "banner": admins[i["relationships"]["user"]["data"]["id"]],
                    }
                else:
                    newList[i["id"]] = {
                        "banid": i["id"],
                        "playername": i["meta"]["player"],
                        "timestamp": i["attributes"]["timestamp"],
                        "expires": i["attributes"]["expires"],
                        "reason": i["attributes"]["reason"],
                        "note": i["attributes"]["note"],
                        "bmid": i["attributes"]["identifiers"][0]["id"],
                        "steamid": i["attributes"]["identifiers"][0]["metadata"][
                            "profile"
                        ]["steamid"],
                        "avatar": i["attributes"]["identifiers"][0]["metadata"][
                            "profile"
                        ]["avatarfull"],
                        "profileurl": i["attributes"]["identifiers"][0]["metadata"][
                            "profile"
                        ]["profileurl"],
                        "banner": "Auto Ban",
                    }
        return newList

    async def compareList(self, banlist):
        newList = {}
        for i in banlist:
            if i not in self.BanListCache:
                newList[i] = banlist[i]
                self.BanListCache.append(i)
        return newList


async def setup(client):
    await client.add_cog(Loops(client))
