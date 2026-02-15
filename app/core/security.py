from passlib.context import CryptContext

# 1. Definiamo il contesto di crittografia
# Specifichiamo che vogliamo usare bcrypt e che deve gestire automaticamente
# la compatibilità con eventuali schemi deprecati in futuro

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str)-> bool:
    """
    Docstring for verify_password
    
    :param plain_password: Description
    :type plain_password: str
    :param hashed_password: Description
    :type hashed_password: str
    :return: Description
    :rtype: bool
    Confronta una password cin chiaro con l'hash salvato nel DB.
    Restituisce True se corrispondono, False altrimenti.
    """

    return pwd_context.verify_(plain_password, hashed_password)

def get_password_hash(password: str)-> str:
    """
    Trasforma una password in chiaro in una hash BCrypt.
    Questa è la funzione da usare durante la registrazione.
    """
    return pwd_context.hash(password)