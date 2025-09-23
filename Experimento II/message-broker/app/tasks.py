import requests

def evento_ping(datos):
    """
    La única función de este worker es notificar al modulo de seguridad.
    """
    try:
        requests.post("http://seguridad:5000/reportar-evento", json=datos)
        print(f"Evento consumido y reportado al modulo de seguridad: {datos}")
    except requests.exceptions.RequestException as e:
        print(f"Error al reportar evento al modulo de seguridad: {e}")
