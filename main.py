from telebot.async_telebot import AsyncTeleBot
import asyncio
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

# Variáveis
api_key = '6937728771:AAHEQM7COusCZYT4hUTHPrqTFkh-nn-P0uY'
admins = ['673195223', '6676616608']
rafael = admins[0]
leonardo = admins[1]
content_on_hold = {
    'userID': [],
    'messageID': [],
    'fileJPG': [],
    'fileMP4': [],
    'download_JPG': [],
    'download_MP4': []
}
chatID = '-1002091660933'

# Inicia bot
bot = AsyncTeleBot(api_key)


# Enviar mensagem de aprovação ou reprovação
async def send_message_verification(data, user_id):
    if data == 'aprovar':
        await bot.send_message(user_id, '''Seu conteúdo foi aprovado e direcionado para o grupo!
                               Fique despreocupada(o) que nenhuma informação pessoal foi compartilhada.''')


# Envia Conteúdo para aprovação
@bot.message_handler(content_types=['photo'])
async def aprovation_photo(message):
    
    # Separa informações
    fileId = message.photo[-1].file_id
    file_info = await bot.get_file(fileId)
    userID = message.from_user.id

    # Adiciona dados do usuário no dicionário
    content_on_hold['userID'].append(f'{userID}')
    content_on_hold['messageID'].append(f'{message.message_id}')
    content_on_hold['fileJPG'].append(fileId)
    content_on_hold['fileMP4'].append(None)
    content_on_hold['download_MP4'].append(None)

    # Adiciona arquivo no dicionário
    content_on_hold['download_JPG'].append(await bot.download_file(file_info.file_path))
    downloaded_file = await bot.download_file(file_info.file_path)

    # Envia informações para aprovação
    await bot.send_message(rafael, f'Conteúdo aguardando aprovação id: #F{message.message_id}\nUserName: @{message.from_user.username}')
    await bot.send_message(leonardo, f'Conteúdo aguardando aprovação id: #F{message.message_id}\nUserName: @{message.from_user.username}')

    # Cria botão com opções "Aprovar" e "Reprovar"
    menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    menu.add(
        KeyboardButton('/aprovar'),
        KeyboardButton('/reprovar'),
        KeyboardButton('/em_espera')                
        )

    # Envia o arquivo para o admin
    await bot.send_photo(rafael, downloaded_file , caption=f'#F{message.message_id}', reply_markup=menu)
    await bot.send_photo(leonardo, downloaded_file , caption=f'#F{message.message_id}',reply_markup=menu)
    
    # Envia confirmação para usuário
    await bot.send_message(userID, 'Seu conteúdo foi enviado para o admin e esta aguardando aprovação.')


@bot.message_handler(content_types=['video'])
async def aprovation_video(message):
    
    # Separa informações
    fileId = message.video.file_id
    file_info = await bot.get_file(fileId)
    userID = message.from_user.id

    # Adiciona dados do usuário no dicionário
    content_on_hold['userID'].append(f'{userID}')
    content_on_hold['messageID'].append(f'{message.message_id}')
    content_on_hold['fileJPG'].append(None)
    content_on_hold['fileMP4'].append(message.video)
    content_on_hold['download_JPG'].append(None)
    

    # Adiciona arquivo no dicionário
    content_on_hold['download_MP4'].append(await bot.download_file(file_info.file_path))
    downloaded_file = await bot.download_file(file_info.file_path)

    # Envia informações para aprovação
    await bot.send_message(rafael, f'Conteúdo aguardando aprovação id: #F{message.message_id}\nUserName: @{message.from_user.username}')
    await bot.send_message(leonardo, f'Conteúdo aguardando aprovação id: #F{message.message_id}\nUserName: @{message.from_user.username}')

    # Cria botão com opções "Aprovar" e "Reprovar"
    menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    menu.add(
        KeyboardButton(f'/aprovar'),
        KeyboardButton(f'/reprovar'),
        KeyboardButton('/em_espera')                
        )

    # Envia o arquivo para o admin
    await bot.send_video(rafael, downloaded_file , caption=f'#F{message.message_id}', reply_markup=menu)
    await bot.send_video(leonardo, downloaded_file , caption=f'#F{message.message_id}', reply_markup=menu)
    
    # Envia confirmação para usuário
    await bot.send_message(userID, 'Seu conteúdo foi enviado para o admin e esta aguardando aprovação.')



@bot.message_handler(commands=['aprovar'])
async def aprove_content(message):
    global content_on_hold

    # Verifica dados das mensagens
    message_id = (message.text.split()[1])
    message_admin = ' '.join(message.text.split()[2:])

    approved_content = None
    
    for content in content_on_hold['messageID']:
        if content == message_id:
            # Recupera informações do conteudo
            index = content_on_hold['messageID'].index(content)
            userId = content_on_hold['userID'][index]
            file_JPG = content_on_hold['fileJPG'][index]
            file_MP4 = content_on_hold['fileMP4'][index]
            downloaded_JPG = content_on_hold['download_JPG'][index]
            downloaded_MP4 = content_on_hold['download_MP4'][index]

            approved_content = {
                'userId': userId,
                'file_JPG': file_JPG,
                'file_MP4': file_MP4,
                'downloaded_JPG': downloaded_JPG,
                'downloaded_MP4': downloaded_MP4
            }

            await bot.send_message(rafael, f'Conteúdo aprovado por: @{message.from_user.username}\nConteúdo ID: {message_id}')
            await bot.send_message(leonardo, f'Conteúdo aprovado por: @{message.from_user.username}\nConteúdo ID: {message_id}')

            if message_admin:
                await bot.send_message(userId, f'Seu conteudo foi aprovado. \nComentario do admin: {message_admin}')
            else:
                await bot.send_message(userId, 'Seu conteudo foi aprovado.')

            # Remove o conteúdo aprovado do dicionário
            content_on_hold['userID'].pop(index)
            content_on_hold['messageID'].remove(content)
            content_on_hold['fileJPG'].pop(index)
            content_on_hold['fileMP4'].pop(index)
            content_on_hold['download_JPG'].pop(index)
            content_on_hold['download_MP4'].pop(index)

    # Envie o conteúdo para o grupo
    if approved_content:
        if approved_content['file_JPG']:
            await bot.send_photo(chatID, approved_content['downloaded_JPG'], caption='Conteudo enviado por inscrito anônimo \nEnvie Seu conteudo para @SecretinhoConteudoBOT ')
        elif approved_content['file_MP4']:
            await bot.send_video(chatID, approved_content['downloaded_MP4'], caption='Conteudo enviado por inscrito anônimo \nEnvie Seu conteudo para @SecretinhoConteudoBOT ')


@bot.message_handler(commands=['reprovar'])
async def reject_content(message):
    # Recebe informações da mensagem
    message_id = message.text.split()[1]

    for content in range(len(content_on_hold['messageID'])):
        if content_on_hold['messageID'][content] == message_id:
            userId = content_on_hold['userID'][content]
            fileId = content_on_hold['fileMP4'][content]  # Corrigido de 'fileID' para 'fileMP4'
            await bot.send_message(rafael, f'Conteúdo reprovado por: @{message.from_user.username}')
            await bot.send_message(leonardo, f'Conteúdo reprovado por: @{message.from_user.username}')
            await bot.send_message(userId, 'Seu conteúdo foi reprovado.')
            await bot.send_message(rafael, f'ID: #{message_id}')
            await bot.send_message(leonardo, f'ID: #{message_id}')
            await bot.send_message(userId, f'ID: #{message_id}')

            # Remove o conteúdo reprovado do dicionário
            del content_on_hold['userID'][content]
            del content_on_hold['messageID'][content]
            del content_on_hold['fileJPG'][content]
            del content_on_hold['fileMP4'][content]
            del content_on_hold['download_file'][content]


@bot.message_handler(commands=['em_espera'])
async def content_list(message):
    await bot.send_message(message.chat.id, 'Conteúdos aguardando aprovação:')
    
    for content_id in content_on_hold['messageID']:
        await bot.send_message(message.chat.id, f'ID: #F{content_id}')


@bot.message_handler(commands='start')
async def apresentation_bot(message):
    await bot.send_message(message.from_user.id, 'Olá! 👋 Sou o SecretinhoConteudoBOT, seu parceiro de envios anônimos! 🤖✉️ Envie-me suas fotos e vídeos, e eu os encaminharei para o grupo Secretinho, garantindo o anonimato total! 🌟✨ Seja parte da diversão de forma discreta. 😎📸🎥 Envie seus conteúdos agora! 🚀📤')

# Mantém interação ativa
async def main():
    try:
        await bot.polling(non_stop=True)
    except Exception as e:
        print(f'Erro: {e}, reconectando...')
        await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(main())