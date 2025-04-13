import logging

# Configuração básica
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("app.log"),     # salva em arquivo
        logging.StreamHandler()             # também no terminal
    ]
)

logger = logging.getLogger("PhonIA")
