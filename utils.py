import threading
from weakref import WeakValueDictionary


class Singleton:    # pylint: disable=no-member
    """
    Singleton decorator to avoid having multiple objects handling the same args
    """
    def __new__(cls, klass):
        # We must use WeakValueDictionary() to let the instances be garbage-collected
        _dict = dict(cls.__dict__, **{'cls': klass, 'instances': WeakValueDictionary()})
        singleton = type(klass.__name__, cls.__bases__, _dict)
        obj = super().__new__(singleton)
        obj.lock = threading.RLock()
        return obj

    def __instancecheck__(self, other):
        return isinstance(other, self.cls)

    def __call__(self, *args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        if key not in self.instances:
            with self.lock:
                if key not in self.instances:
                    instance = self.cls.__call__(*args, **kwargs)
                    self.instances[key] = instance
        return self.instances[key]
