import requests

def heartbeat_ping(datos):
    """
    La única función de este worker es notificar al monitor.
    """
    try:
        requests.post("http://monitor:5000/reportar-heartbeat", json=datos)
        print(f"Heartbeat consumido y reportado al monitor: {datos}")
    except requests.exceptions.RequestException as e:
        print(f"Error al reportar heartbeat al monitor: {e}")
