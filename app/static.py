from config import *

# PERSONAL DATAS
AUTHOR_NAME = "Giyu"
AUTHOR_TWITTER_URL = "https://twitter.com/giyuu__"
AUTHOR_ICON_URL = "https://cdn.discordapp.com/avatars/467363532929892367/29eda65afa43e72e2577e8d41a2a1913"

BOT_NAME = "Jaskier"
BOT_DESC = "Um bot de música simples"
BOT_GITHUB_URL = "https://github.com/lucasataides/Jaskier"
BOT_INVITE_LINK = "https://discord.com/oauth2/authorize?client_id=888111878126043156&scope=bot&permissions=6479662400"

COMMANDS = {
    "play [link ou busca]": "Toca uma música",
    "pause": "Pausa a música atual",
    "resume": "Volta a tocar a música atual",
    "stop": "Para a sessão",
    "skip": "Pula a música atual",
    "prev": "Toca a música anterior",
    "queue": f"Mostra as próximas {MAX_SONG_PRELOAD} músicas",
    "history": "Mostra as músicas que já foram tocadas nessa sessão",
    "clear": "Esvazia a fila",
    "songinfo": "Mostra informações sobre a música atual",
    "volume <valor de 0 a 100>": "Mostra o volume atual ou altera-o",
    "loopsong": "Ativa / desativa o loop da música atual",
    "shuffle": "Embaralha a fila atual",
    "ping": "Latência do bot",
    "help": "Mostra os comandos disponíveis",
    "info": "Informações sobre a máquina",
    "invite": "Como botar o Jaskier no seu servidor"
}