import discord
import asyncio
import random
import time

class MyClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.last_time = time.time()
        self.accepted_users = ['cheeseooze#1319', 'Snade#8050', 'catbugisback#7516']
        self.muted_users = []
        self.warnings = {}
        self.risovka_reply = []
        self.risovkas = []


    def check_command(self, message, command):
        if (str(message.author) in self.accepted_users) and (message.content.startswith(command)):
            return True
        else:
            return False


client = MyClient()


async def save_user_warns():
    await client.wait_until_ready()
    while not client.is_closed:
        if len(client.warnings) > 10:
            with open("user_warnings.txt", "w") as f:
                for server in client.servers:
                    if server.name == 'Раскрашенная Камера':
                        for member in server.members:
                            try:
                                count = client.warnings[member]
                            except Exception:
                                count = 0
                            f.write(member.id + ":" + str(count) + '\n')
        await asyncio.sleep(3600)


async def save_ignoring_words():
    await client.wait_until_ready()
    while not client.is_closed:
        if len(client.risovkas):
            with open("user_warnings.txt", "w") as f:
                for word in client.risovkas:
                    f.write(word)
        await asyncio.sleep(3600)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    with open("user_warnings.txt", "r") as f:
        for server in client.servers:
            if server.name == 'Раскрашенная Камера':
                for member in server.members:
                    client.warnings[member] = 0
                for channel in server.channels:
                    if channel.id == '374703129264128000':
                        client.tech_channel = channel


    with open("user_warnings.txt", "r") as f:
        for line in f:
            t = line.split(":")
            for server in client.servers:
                if server.name == 'Раскрашенная Камера':
                    for member in server.members:
                        if member.id == t[0]:
                            client.warnings[member] = int(t[1])
                            break



    with open("risovka_reply.txt", "r") as f:
        for line in f:
            client.risovka_reply.append(f.readline())

    with open("ignoring_words.txt", "r") as f:
        for line in f:
            client.risovkas.append(line[:-1])


async def mute_user(client, message, user, time):
    for member in message.server.members:
        if member.name + "#" + member.discriminator == user:
            client.muted_users.append(member)
            print("Muted " + member.name + " for " + str(time) + " seconds")
            await asyncio.sleep(time)
            try:
                client.muted_users.remove(member)        
            except Exception:
                pass


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author in client.muted_users:
        await client.delete_message(message)
        return

    if client.check_command(message, '!commands'):
        strings = ['!say <msg> - отправить текстовое сообщение от имени бота', '!commands - вывести список команд', 
        '!ban @<user> - забанить юзера (через меншн)', '!warn @<user> <msg> - вынести предупреждение юзеру (через меншн) с сообщением (оно может быть пустым)',
        '!unwarn @<user> - убрать предупреждение с юзера (через меншн)', '!mute <user> - замтютит юзера (без меншена)', 
        '!unmute <user> - размутить пользователя (без меншена)', '!muted_list - вывести список замьюченных пользователей', 
        '!ignore_list - вывести список игнорируемых слов','!add_word_ignore <word>- добавить в фильтр слово']
        answer = '```Список команд:\n' + '\n'.join(strings) + '\n```'
        await client.send_message(message.channel, answer)
        return

    if client.check_command(message, '!add_word_ignore'):
        cmd = message.content.split(' ')
        client.risovkas.append(cmd[1])
        await client.send_message(client.tech_channel, 'Слово {} добавлено в список инорируемых'.format(cmd[1]))
        return

    if client.check_command(message, '!ignore_list'):
        ans = 'Запрещенные слова: [', ', '.join(client.risovkas) + ']'
        await client.send_message(message.channel, ans)
        return

    if client.check_command(message, '!say'):
        await client.delete_message(message)
        await client.send_message(message.channel, message.content[4:])
        return


    if client.check_command(message, '!count_warns'):
        warn_number = 0
        mention = ''
        for member in message.server.members:
            if member.id == message.content[15:-1]:
                warn_number = client.warnings[member]
                mention = member.mention
                break

        warns = '[' + warn_number*' :rage: ' + (3-warn_number)*' :white_large_square: ' + '] '

        answer = "Количество предупреждений у {} - {}".format(mention, warns)
        await client.send_message(message.channel, answer)
        return


    if client.check_command(message, '!ban'):
        for member in message.server.members:
            if member.id == message.content[7:-1]:
                await client.ban(member, 0)
                return

    if client.check_command(message, '!warn'):
        cmd = message.content.split(' ')
        cmd[1] = cmd[1][2:-1]
        warn_number = 0
        mention = ''
        for member in message.server.members:
            # if member.name + "#" + member.discriminator == cmd[1]:
            if member.id == cmd[1]:
                if member in client.warnings:
                    client.warnings[member] += 1
                else:
                    client.warnings[member] = 1
                mention = member.mention
                warn_number = client.warnings[member]
                if client.warnings[member] == 3:
                    await client.ban(member, 0)
                    client.warnings[member] = 0
                    break

        warns = '[' + warn_number*' :rage: ' + (3-warn_number)*' :white_large_square: ' + '] '
        if len(cmd) > 2:
            reason = "Причина: '" + ' '.join(cmd[2:]) + "'"
        else:
            reason = ''

        answer = "{} вынесено предупреждение {}".format(mention, warns) + reason

        await client.send_message(message.channel, answer)

        return


    if client.check_command(message, '!unwarn'):
        cmd = message.content.split(' ')
        cmd[1] = cmd[1][2:-1]
        warn_number = 0
        mention = ''
        for member in message.server.members:
            if member.id == cmd[1]:
                client.warnings[member] -= 1
                mention = member.mention
                warn_number = client.warnings[member]

        warns = '[' + warn_number*' :rage: ' + (3-warn_number)*' :white_large_square: ' + '] '
        if len(cmd) > 2:
            reason = "Причина: '" + ' '.join(cmd[2:]) + "'"
        else:
            reason = ''
        answer = "{} убрано предупреждение {}".format(mention, warns) + reason
        await client.send_message(message.channel, answer)
        return

    if client.check_command(message, '!muted_list'):
        res = '['
        for user in client.muted_users:
            res = res + user.name + ','
        res += ']'
        await client.send_message(message.channel, res)     
        return


    if client.check_command(message, '!mute'):
        cmd = message.content.split(' ')
        res = await mute_user(client, message, cmd[1], int(cmd[2]))
        return

    if client.check_command(message, '!risovka_pic'):
        await client.send_file(message.channel, 'risovka1.jpg')

    if client.check_command(message, '!unmute'):
        cmd = message.content.split(' ')
        try:
            for member in message.server.members:
                if member.name + "#" + member.discriminator == cmd[1]:
                    client.muted_users.remove(member)
        except Exception:
            await client.send_message(message.channel, "Пользователь " + cmd[1] + " не замьючен")
        return



    if any(risovka in message.content.lower() for risovka in client.risovkas):
        print(str(message.author) + ": " + (message.content))
        ans = message.channel.name + "> " + message.author.name + ":" + message.content
        await client.send_message(client.tech_channel, ans)
        curr_time = time.time()
        if curr_time - client.last_time > 5:
            await client.send_message(message.channel, random.choice(client.risovka_reply))
            client.last_time = curr_time
        await client.delete_message(message)



client.loop.create_task(save_user_warns())
client.loop.create_task(save_ignoring_words())
client.run(token)