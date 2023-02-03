# -*- coding: utf-8 -*-

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
    print("PRET !")


@tree.command(name = "assigner_role", description = "Donne un role aux personnes presentes dans le fichier .csv")
@commands.has_permissions(manage_roles=True)
@app_commands.describe(fichier="Fichier .csv à utiliser pour donné le role", role="Role à donner aux personnes présentes dans le fichier", supprimer="Le role sera retiré aux personnes l'ayant actuellement")
async def assign_role(ctx, fichier: discord.Attachment, role : discord.Role, supprimer : bool):

    await ctx.response.send_message(content="Chargement ...", ephemeral=True)
    
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

            await ctx.edit_original_response(content=(f"Role retiré à : {OldMemberTxt}\n\nNouveau role donné à : {NewMenberTxt}\n\nPersonnes qui n'ont pas été trouvé sur le discord : {not_found}"))

        else:

            await ctx.edit_original_response(content=(f"Personnes qui n'ont pas été trouvé sur le discord : {not_found}"))

    except Exception as e:

        print(e)
        await ctx.edit_original_response(content=("Le fichier n'est pas lisible. Veuillez verifier qu'il s'agit bien d'un .csv uniquement, les autres types de fichiers ne sont pas pris en charge"))


@tree.command(name = "transferer_role", description = "Transfert un rôle aux personnes possedant un autre role")
@commands.has_permissions(manage_roles=True)
@app_commands.describe(ancien_role="Role des personnes a transferer", nouveau_role="Role à donner", supprimer="Supprimer le role initial des personnes à transferer")
async def transfert_role(ctx, ancien_role : discord.Role, nouveau_role : discord.Role,supprimer : bool):

    await ctx.response.send_message(content="Chargement ...", ephemeral=True)

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

        await ctx.edit_original_response(content=(f'Role retiré à : {OldMemberTxt}\n\nNouveau role donné à : {NewMenberTxt}'))

    else:

        await ctx.edit_original_response(content=(f'Nouveaux role donné à : {NewMenberTxt}'))


@tree.command(name = "creer_categorie", description = "Créer une catégorie type avec les channels et les différentes permissions")
@commands.has_permissions(manage_messages=True)
@app_commands.describe(nom_categorie="Nom de la catégorie a créer", role="Role ayant accès a cette catégorie", role2="Second role ayant accès a la categorie")
async def create_category(ctx, nom_categorie : str, role : discord.Role, role2 : discord.Role = None):

    server = ctx.guild
    name_cat = f" {nom_categorie} "

    await ctx.response.send_message(content="Chargement ...", ephemeral=True)

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

        await ctx.edit_original_response(content=(f'La catégorie {name_cat.upper()} a bien été créée pour le role {role} !'),)

    else:

        await ctx.edit_original_response(content=(f'La catégorie {name_cat.upper()} a bien été créée pour les roles {role} et {role2} !'))


@tree.command(name = "supprimer_categorie", description = "Supprime la catégorie ainsi que tous les channels la composant")
@commands.has_permissions(manage_messages=True)
@app_commands.describe(nom_categorie="Nom de la catégorie a supprimer")
async def delete_category(ctx, nom_categorie : str):

    await ctx.response.send_message(content="Chargement ...", ephemeral=True)

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

            await ctx.edit_original_response(content=(f"La catégorie {name_cat.upper()} n'existe pas !"))

        else:

            try:

                for channel in category_object.channels:

                    await channel.delete()

                await category_object.delete()

            except discord.errors.NotFound as e:
                
                print(e)
                
            await ctx.edit_original_response(content=(f'La catégorie {name_cat.upper()} a bien été supprimée !'))
        
    except AttributeError:

        await ctx.edit_original_response(content=(f"La catégorie {name_cat.upper()} n'existe pas !"))
    

@tree.command(name = "creer_channel", description = "Créer un nouveau channel dans la catégorie avec les permissions de cette dernière")
@commands.has_permissions(manage_messages=True)
@app_commands.describe(nom_channel="Nom du channel a créer", nom_categorie="Nom de la catégorie dans lequel il doit être situé", acces_pedago="Donner l'accès au role Pédago")
async def create_channel(ctx, nom_channel : str, nom_categorie : str, acces_pedago: bool):

    await ctx.response.send_message(content="Chargement ...", ephemeral=True)

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

    if acces_pedago == True:
        pedago = discord.utils.get(ctx.guild.roles,name="Team Pedago IPI")
        await discord.utils.get(ctx.guild.channels, name=nom_channel.lower()).set_permissions(target=pedago, read_messages=True, send_messages=True, connect=True, speak=True)

    await ctx.edit_original_response(content=(f'Le channel {nom_channel.lower()} a bien été créé dans la categorie {name_cat.upper()} !'))


@tree.command(name = "supprimer_channel", description = "Supprimer un channel d'une catégorie")
@commands.has_permissions(manage_messages=True)
@app_commands.describe(nom_channel="Nom du channel a supprimer", nom_categorie="Nom de la catégorie dans lequel il est situé")
async def delete_channel(ctx, nom_channel : str, nom_categorie : str):

    await ctx.response.send_message(content="Chargement ...", ephemeral=True)

    name_cat = f" {nom_categorie} "
    while len(name_cat) <= 27:

        name_cat = f"={name_cat}="

    try:

        category_object = discord.utils.get(ctx.guild.categories, id=(discord.utils.get(ctx.guild.categories, name=name_cat.upper()).id))
    
        if category_object is None:

            await ctx.edit_original_response(content=(f"La catégorie {name_cat.upper()} n'existe pas !"))

        else:

            try:

                for channels in category_object.channels:

                    if str(channels) == nom_channel:

                        await channels.delete()

            except discord.errors.NotFound as e:

                print(e)
                
            await ctx.edit_original_response(content=(f'Le channel {nom_channel.lower()} situé dans la catégorie {name_cat.upper()} a bien été supprimé !'))
        
    except AttributeError as e:

        print(e)
        await ctx.edit_original_response(content=(f"Le channel {nom_channel.lower()} n'existe pas dans la catégorie {name_cat.upper()}."))
    


client.run(jsonObject["DISCORD_TOKEN"])