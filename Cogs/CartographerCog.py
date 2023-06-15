import discord
from discord.ext import commands
import os
import json
import ast
import sys
from Cogs.StoryBoardDisplayCog import ColorPicker
from Cogs.Storyboard import SBImageAssembly




FilePath = os.path.dirname(os.path.abspath(__file__))
intents = discord.Intents.all()
bot = discord.Client(intents=intents)


def LoadMap():
    if sys.platform == "linux" or sys.platform == "linux2":
        with open(f"{FilePath}/Files/Map.json", "r") as JSON:
            return json.load(JSON)
    if sys.platform == "win32" or sys.platform == "win64":
        with open(f"{FilePath}\\Files\\Map.json", "r") as JSON:
            return json.load(JSON)


class NaniteBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.is_owner()
    @commands.command(aliases=["Make", "Make The", "Make My", "Create The", "Create My", "Let There Be"],
                      pass_context=True)
    async def Create(self, ctx, PlaceToMake):
        await ctx.message.delete()
        self.Map=LoadMap()
        everyone = ctx.guild.default_role
        NewLocation = await ctx.guild.create_category(PlaceToMake)
        for Location in self.Map[PlaceToMake]:
            NewChannel = await ctx.guild.create_text_channel(f"{Location}", overwrites={
                everyone: discord.PermissionOverwrite(read_messages=True, send_messages=False)},
                                                             topic=self.Map[PlaceToMake][Location]["Topic"],
                                                             category=NewLocation)
            LocationEmbed = discord.Embed(colour=0x31f25c,
                                  description=self.Map[PlaceToMake][Location]["Description"])
            try:
                if sys.platform == "linux" or sys.platform == "linux2":
                    Image=discord.File(f"{FilePath}/Files/Images/Locations/{self.Map[PlaceToMake][Location]['Image']}.jpg")
                    LocationEmbed.set_image(url=f"attachment://{FilePath}/Files/Images/Locations/{self.Map[PlaceToMake][Location]['Image']}.jpg")
                if sys.platform == "win32" or sys.platform == "win64":
                    Image=discord.File(f"{FilePath}\\Files\\Images\\Locations\\{self.Map[PlaceToMake][Location]['Image']}.jpg")
                    LocationEmbed.set_image(url=f"attachment://{FilePath}\\Files\\Images\\Locations\\{self.Map[PlaceToMake][Location]['Image']}.jpg")
            except FileNotFoundError:
                if sys.platform == "linux" or sys.platform == "linux2":
                    Image=discord.File(f"{FilePath}/Files/Images/Locations/{self.Map[PlaceToMake][Location]['Image']}.png")
                    LocationEmbed.set_image(url=f"attachment://{FilePath}/Files/Images/Locations/{self.Map[PlaceToMake][Location]['Image']}.png")
                if sys.platform == "win32" or sys.platform == "win64":
                    Image=discord.File(f"{FilePath}\\Files\\Images\\Locations\\{self.Map[PlaceToMake][Location]['Image']}.png")
                    LocationEmbed.set_image(url=f"attachment://{FilePath}\\Files\\Images\\Locations\\{self.Map[PlaceToMake][Location]['Image']}.png")


            LocationView = discord.ui.View()
            for NPC in self.Map[PlaceToMake][Location]["NPC"]:
                print(NPC)
                NPCButton=discord.ui.Button(label=NPC)
                async def NPCButtonCallback(interaction):
                    Choices = SBImageAssembly(NPC,"Start")
                    TempFile = discord.File(f"{FilePath}\\Files\\Images\\TEMP.png", filename="TEMP.png")
                    SBView = discord.ui.View()
                    Inventory = {}
                    for each in Choices:
                        if each == "Scenario":
                            pass
                        else:
                            Style = ColorPicker(Choices, each)
                            ChoiceButton = discord.ui.Button(label=each,
                                                             custom_id=f"{Choices['Scenario']},{Choices[each]['Destination']},{Inventory}",
                                                             style=Style)
                            ChoiceButton.callback = self.ChoiceButtonCallback
                            SBView.add_item(ChoiceButton)
                    await interaction.response.send_message(ephemeral=True, file=TempFile, view=SBView)

                LocationView.add_item(NPCButton)
                NPCButton.callback = NPCButtonCallback

            await NewChannel.send(embed=LocationEmbed,view=LocationView,file=Image)

    async def ChoiceButtonCallback(self,interaction):
        Data = interaction.data['custom_id'].split(",")
        Inventory = ast.literal_eval(Data[2])
        try:
            if Data[3]!=None:
                InvintoryUpdate = Data[3].split(":")
                Items = InvintoryUpdate[1].split(",")
                if InvintoryUpdate[0]=="Price":
                    for each in Items:
                        Inventory.pop(each,None)
                if InvintoryUpdate[0]=="Reward":
                    for each in Items:
                        Inventory[each] = 1
        except IndexError:
            pass
        Choices = SBImageAssembly(Data[0], Data[1])
        TempFile = discord.File(f"{FilePath}\\Files\\Images\\TEMP.png", filename="TEMP.png")
        ChoiceView = discord.ui.View()
        for each in Choices:
            if each == "Scenario":
                pass
            else:
                Style = ColorPicker(Choices, each)
                if each == "End":
                    EndButton = discord.ui.Button(label=each,
                                custom_id=f"{Choices['Scenario']},{Choices[each]['Destination']},{Inventory}")
                    EndButton.callback = self.EndButtonCallback
                    ChoiceView.add_item(EndButton)
                if each == "End Conversation":
                    StopButton = discord.ui.Button(label=each)
                    StopButton.callback = self.StopButtonCallback
                    ChoiceView.add_item(StopButton)
                elif Choices[each]['Requirement'] != "":
                    if Choices[each]['Requirement'] in Inventory:
                        if Choices[each]['Price'] != "":
                            if Choices[each]['Price'] in Inventory:

                                ChoiceButton = discord.ui.Button(label=f"{each}  Requirement:{Choices[each]['Requirement']}  Cost:{Choices[each]['Price']}",
                                                                 custom_id=f"{Choices['Scenario']},{Choices[each]['Destination']},{Inventory},Price:{Choices[each]['Price']}",
                                                             style=Style)
                        else:
                            ChoiceButton = discord.ui.Button(label=f"{each}"
                                                                   f" Requirement:{Choices[each]['Requirement']}",
                                                             custom_id=f"{Choices['Scenario']},{Choices[each]['Destination']},{Inventory}",
                                                             style=Style)
                        ChoiceButton.callback = self.ChoiceButtonCallback
                        ChoiceView.add_item(ChoiceButton)

                elif Choices[each]['Price'] != "":
                    if Choices[each]['Price'] in Inventory:
                        ChoiceButton = discord.ui.Button(label=f"{each}  Cost:{Choices[each]['Price']}",
                                                         custom_id=f"{Choices['Scenario']},{Choices[each]['Destination']},{Inventory},Price:{Choices[each]['Price']}",
                                                         style=Style)
                        ChoiceButton.callback = self.ChoiceButtonCallback
                        ChoiceView.add_item(ChoiceButton)

                elif Choices[each]['Reward'] != "":
                    ChoiceButton = discord.ui.Button(label=f"{each}            Reward:{Choices[each]['Reward']}",
                                                     custom_id=f"{Choices['Scenario']},{Choices[each]['Destination']},{Inventory},Reward:{Choices[each]['Reward']}",
                                                     style=Style)
                    ChoiceButton.callback = self.ChoiceButtonCallback
                    ChoiceView.add_item(ChoiceButton)

                else:
                    ChoiceButton = discord.ui.Button(label=each,
                                                     custom_id=f"{Choices['Scenario']},{Choices[each]['Destination']},{Inventory}",
                                                     style=Style)
                    ChoiceButton.callback = self.ChoiceButtonCallback
                    ChoiceView.add_item(ChoiceButton)

        await interaction.response.edit_message(attachments=[TempFile], view=ChoiceView)

    async def EndButtonCallback(self,interaction):
        Data = interaction.data['custom_id'].split(",")
        await interaction.response.edit_message(view=None)
        await interaction.channel.send(
            f"{interaction.user.name} has finished {Data[0]} with a ranking of {Data[1]} and found {Data[2]}")

    async def StopButtonCallback(self,interaction):
        await interaction.response.edit_message(delete_after=.1)



async def setup(bot):
    await bot.add_cog(NaniteBot(bot))


