"""Excepciones de negocio que los controladores convierten en mensajes para el usuario."""


class ErrorNegocio(Exception):
    """Error esperado de una regla de negocio."""


class ValidacionError(ErrorNegocio):
    def __init__(self, campos: dict[str, str]):
        self.campos = campos
        super().__init__("Revisa los campos marcados: " + ", ".join(campos))


class DocumentoDuplicadoError(ErrorNegocio):
    def __init__(self, documento: str):
        super().__init__(f"El documento {documento} ya se encuentra registrado en el sistema.")


class CorreoDuplicadoError(ErrorNegocio):
    def __init__(self, correo: str):
        super().__init__(f"El correo {correo} ya está asociado a otra cuenta.")


class CredencialesInvalidasError(ErrorNegocio):
    def __init__(self):
        super().__init__("Usuario o contraseña incorrectos.")


class NoEncontradoError(ErrorNegocio):
    pass
