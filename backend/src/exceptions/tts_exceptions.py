class TTSError(Exception):
    """
    Базовая ошибка TTS-сервиса.
    """
    pass


class TTSModelNotLoadedError(TTSError):
    """
    Ошибка, если TTS-модель не была передана в сервис.
    """
    pass


class TTSSynthesisError(TTSError):
    """
    Ошибка, если во время генерации аудио что-то пошло не так.
    """
    pass