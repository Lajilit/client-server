import json

from constants import MAX_PACKAGE_LENGTH, ENCODING


def send_message(socket, message):
    """
    The function turns the message into a json string,
    encodes it and forwards it to the specified socket
    :param socket: receiver socket
    :param message: forwarded message: dict
    """
    json_message = json.dumps(message)
    encoded_message = json_message.encode(ENCODING)
    socket.send(encoded_message)


def get_message(socket):
    """
    The function accepts the sender's socket,
    receives the forwarded message from it,
    decodes using the standard encoding,
    turns the received json string into a dictionary and
    returns this dict
    :param socket: sender's socket
    :return: received message: dict
    """
    encoded_message = socket.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_message, bytes):
        decoded_message = encoded_message.decode(ENCODING)
        message = json.loads(decoded_message)
        if isinstance(message, dict):
            return message
        raise ValueError
    raise ValueError
