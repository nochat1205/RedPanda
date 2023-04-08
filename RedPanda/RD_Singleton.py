class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            BaseClass= super(Singleton, cls)
            cls._instance = BaseClass.__new__(cls, *args, **kwargs)

        return cls._instance
