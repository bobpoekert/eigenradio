class EPERM(OSError):
    pass

class ENOENT(OSError):
    pass

class EINVAL(OSError):
    pass

class EPIPE(OSError):
    pass

class EAGAIN(OSError):
    pass

error_codes = {
        1:EPERM,
        2:ENOENT,
        22:EINVAL,
        32:EPIPE,
        11:EAGAIN}

def raise_socket_error(code, text='socket error'):
    try:
        raise error_codes[code](code, text)
    except KeyError:
        raise OSError(code, text)
