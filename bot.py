import discord,re,json,urllib.request
from discord.ext import commands
from discord import app_commands

intents = discord.Intents().all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

with open("data.json") as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")


@tree.command(name = "assigner_role", description = "Assign the role given to all the persons in the .csv file")
@commands.has_permissions(manage_roles=True)
@app_commands.describe(fichier="File to use for reading", role="Role to assign to the persons in the .csv file", supprimer="Do you want to delete the persons who have the role at the moment ?")
async def assign_role(ctx, fichier: discord.Attachment, role : discord.Role, supprimer : bool):

    await ctx.response.send_message(content="Loading ...", ephemeral=True)
    
    if supprimer==True:

        OldMemberID = [m.id for m in role.members]
        OldMember = [m.display_name for m in role.members]
        for member in OldMemberID:

            await ctx.guild.get_member(member).remove_roles(role)

        OldMemberTxt = ', '.join(OldMember)

    member_list = []

    for member in ctx.guild.members:

        member_list.append(member.display_name.replace(" ", "").lower())
        member_list.append(member.id)

    try:

        all_file = []
        for row in urllib.request.urlopen(urllib.request.Request(url=str(fichier), headers={'User-Agent': 'Mozilla/5.0'})):

            element_list=[]
            for element in re.split(',|\n|\r|;|\ufeff', row.decode('utf-8')):

                if element != "":

                    element_list.append(element)

            all_file.append(element_list)
        
        not_found=[]
        for element_list in all_file:

            try:

                element_list[1]
                if ((str(element_list[0]) + str(element_list[1])).replace(" ", "").lower() in member_list) or ((str(element_list[1]) + str(element_list[0])).replace(" ", "").lower() in member_list) :

                    try:

                        await (ctx.guild.get_member(member_list[member_list.index((str(element_list[0]) + str(element_list[1])).replace(" ", "").lower())+1])).add_roles(role)

                    except:

                        await (ctx.guild.get_member(member_list[member_list.index((str(element_list[1]) + str(element_list[0])).replace(" ", "").lower())+1])).add_roles(role)

                else:

                    not_found.append(str(element_list[0]) + " " + str(element_list[1]))

            except IndexError:

                pass

        not_found = ', '.join(not_found)
        NewMenberTxt = ', '.join([m.display_name for m in role.members])

        if supprimer==True:

            await ctx.edit_original_response(content=(f'Removed role to : {OldMemberTxt}\n\nAssign role to : {NewMenberTxt}\n\nPerson(s) not found in the file : {not_found}'))

        else:

            await ctx.edit_original_response(content=(f'Person(s) not found in the file : {not_found}'))

    except Exception as e:

        print(e)
        await ctx.edit_original_response(content=("File not readable (.csv)"))


@tree.command(name = "transferer_role", description = ".csv file reader")
@commands.has_permissions(manage_roles=True)
@app_commands.describe(ancien_role="Person who have this role will be given the new one", nouveau_role="Role to assign", supprimer="Do you want to delete the persons who have the role at the moment ? (yes /no)")
async def transfert_role(ctx, ancien_role : discord.Role, nouveau_role : discord.Role,supprimer : bool):

    await ctx.response.send_message(content="Loading ...", ephemeral=True)

    OldMemberID = [m.id for m in ancien_role.members]
    OldMember = [m.display_name for m in ancien_role.members]
    OldMemberTxt = ', '.join(OldMember)

    if supprimer==True:

        for member in OldMemberID:

            await ctx.guild.get_member(member).remove_roles(ancien_role)
    
    for member in OldMemberID:

            await ctx.guild.get_member(member).add_roles(nouveau_role)

    NewMenberTxt = ', '.join([m.display_name for m in nouveau_role.members])
    if supprimer == True:

        await ctx.edit_original_response(content=(f'Removed role for : {OldMemberTxt}\n\nAssign the new role for : {NewMenberTxt}'))

    else:

        await ctx.edit_original_response(content=(f'Assign the new role for : {NewMenberTxt}'))


@tree.command(name = "creer_categorie", description = "Create the basic category with the channels and permissions")
@commands.has_permissions(manage_messages=True)
@app_commands.describe(nom_categorie="Name of the category you want to create", role="Role you want to give acces to this category", role2="Role you also want to give acces to this category")
async def create_category(ctx, nom_categorie : str, role : discord.Role, role2 : discord.Role = None):

    server = ctx.guild
    name_cat = f" {nom_categorie} "

    await ctx.response.send_message(content="Loading ...", ephemeral=True)

    while len(name_cat) <= 27:

        name_cat = f"={name_cat}="

    tmp=""
    for letter in nom_categorie:
        if letter != " ":
            tmp+=letter
        else:
            tmp+="-"

    nom_categorie = tmp
    await server.create_category(name=name_cat.upper())

    category_object = discord.utils.get(ctx.guild.categories, name=name_cat.upper())
    await category_object.set_permissions(target=role, read_messages=True, send_messages=True, connect=True, speak=True)

    if role2 != None:

        await category_object.set_permissions(target=role2, read_messages=True, send_messages=True, connect=True, speak=True)

    await category_object.set_permissions(ctx.guild.default_role, read_messages=False, connect=False)

    await server.create_text_channel(name="général-"+nom_categorie.lower(),category=category_object)
    await server.create_text_channel(name="pédago-"+nom_categorie.lower(),category=category_object)

    pedago = discord.utils.get(ctx.guild.roles,name="Team Pedago IPI")
    await discord.utils.get(ctx.guild.channels, name="pédago-"+nom_categorie.lower()).set_permissions(target=pedago, read_messages=True, send_messages=True, connect=True, speak=True)

    await server.create_text_channel(name="only-you",category=category_object)
    await server.create_voice_channel(name="général-vocal",category=category_object)
    if role2==None:

        await ctx.edit_original_response(content=(f'Category {name_cat.upper()} created for {role} !'),)

    else:

        await ctx.edit_original_response(content=(f'Category {name_cat.upper()} created for {role} and {role2} !'))


@tree.command(name = "supprimer_categorie", description = "Delete the category and all the channels inside")
@commands.has_permissions(manage_messages=True)
@app_commands.describe(nom_categorie="Name of the category you want to erase")
async def delete_category(ctx, nom_categorie : str):

    await ctx.response.send_message(content="Loading ...", ephemeral=True)

    name_cat = f" {nom_categorie} "
    while len(name_cat) <= 27:

        name_cat = f"={name_cat}="

    tmp=""
    for letter in nom_categorie:

        if letter != " ":

            tmp+=letter

        else:

            tmp+="-"

    nom_categorie = tmp

    try:

        category_object = discord.utils.get(ctx.guild.categories, id=(discord.utils.get(ctx.guild.categories, name=name_cat.upper()).id))
    
        if category_object is None:

            await ctx.edit_original_response(content=(f"Category {name_cat.upper()} doesn't exist !"))

        else:

            try:

                for channel in category_object.channels:

                    await channel.delete()

                await category_object.delete()

            except discord.errors.NotFound as e:
                
                print(e)
                
            await ctx.edit_original_response(content=(f'Category {name_cat.upper()} deleted !'))
        
    except AttributeError:

        await ctx.edit_original_response(content=(f"Category {name_cat.upper()} doesn't exist !"))
    

@tree.command(name = "creer_channel", description = "Create a new channel inside a category and set the permissions")
@commands.has_permissions(manage_messages=True)
@app_commands.describe(nom_channel="Name of the channel you want to create", nom_categorie="Category you want to the channel to be in")
async def create_channel(ctx, nom_channel : str, nom_categorie : str):

    await ctx.response.send_message(content="Loading ...", ephemeral=True)

    server = ctx.guild
    tmp=""

    for letter in nom_channel:

        if letter != " ":

            tmp+=letter

        else:

            tmp+="-"

    name_cat = f" {nom_categorie} "
    while len(name_cat) <= 27:

        name_cat = f"={name_cat}="

    category_object = discord.utils.get(ctx.guild.categories, name=name_cat.upper())

    await server.create_text_channel(name=nom_channel.lower(),category=category_object)

    pedago = discord.utils.get(ctx.guild.roles,name="Team Pedago IPI")
    await discord.utils.get(ctx.guild.channels, name=nom_channel.lower()).set_permissions(target=pedago, read_messages=True, send_messages=True, connect=True, speak=True)

    await ctx.edit_original_response(content=(f'Channel {nom_channel.lower()} created in category {name_cat.upper()} !'))


@tree.command(name = "supprimer_channel", description = "Delete a channel inside a category")
@commands.has_permissions(manage_messages=True)
@app_commands.describe(nom_channel="Name of the channel you want to erase", nom_categorie="Category where the channel is")
async def delete_channel(ctx, nom_channel : str, nom_categorie : str):

    await ctx.response.send_message(content="Loading ...", ephemeral=True)

    name_cat = f" {nom_categorie} "
    while len(name_cat) <= 27:

        name_cat = f"={name_cat}="

    try:

        category_object = discord.utils.get(ctx.guild.categories, id=(discord.utils.get(ctx.guild.categories, name=name_cat.upper()).id))
    
        if category_object is None:

            await ctx.edit_original_response(content=(f"Category {name_cat.upper()} doesn't exist !"))

        else:

            try:

                for channels in category_object.channels:

                    if str(channels) == nom_channel:

                        await channels.delete()

            except discord.errors.NotFound as e:

                print(e)
                
            await ctx.edit_original_response(content=(f'Channel {nom_channel.lower()} deleted in category {name_cat.upper()} !'))
        
    except AttributeError as e:

        print(e)
        await ctx.edit_original_response(content=(f"Channel {nom_channel.lower()} doesn't exist in category {name_cat.upper()}"))
    


client.run(jsonObject["DISCORD_TOKEN"])