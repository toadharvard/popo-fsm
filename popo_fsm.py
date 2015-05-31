import collections
import six
from functools import wraps

class TransitionNotAllowed(Exception):
    """Raise when a transition is not allowed."""


class FSMMeta(object):
    def __init__(self, field_name):
        self.field_name = field_name
        self.transitions = collections.defaultdict()
        self.conditions = collections.defaultdict()

    def current_state(self, instance):
        return getattr(instance, self.field_name)

    def next_state(self, instance):
        return self.transitions.get(self.current_state(instance)) or self.transitions.get('*')

    def has_transition(self, instance):
        return self.next_state(instance) is not None

    def conditions_met(self, instance, *args, **kwargs):
        return all(map(lambda f: f(instance, *args, **kwargs), self.conditions[self.next_state(instance)]))

    def to_next_state(self, instance):
        setattr(instance, self.field_name, self.next_state(instance))


def transition(field, source='*', target=None, conditions=()):
    def inner_transition(func):
        if not hasattr(func, '_sa_fsm'):
            setattr(func, '_sa_fsm', FSMMeta(field))
        if isinstance(source, collections.Sequence) and not isinstance(source, six.string_types):
            for state in source:
                func._sa_fsm.transitions[state] = target
        else:
            func._sa_fsm.transitions[source] = target
        func._sa_fsm.conditions[target] = conditions

        @wraps(func)
        def _change_state(instance, *args, **kwargs):
            meta = func._sa_fsm
            if not meta.has_transition(instance):
                raise TransitionNotAllowed('Cant switch from %s using method %s'
                                           % (meta.current_state(instance), func.__name__))
            for condition in conditions:
                if not condition(instance, *args, **kwargs):
                    return False
            func(instance, *args, **kwargs)
            meta.to_next_state(instance)

        return _change_state

    if not target:
        raise ValueError('Result state not specified')
    return inner_transition


def can_proceed(bound_method, *args, **kwargs):
    if not hasattr(bound_method, '_sa_fsm'):
        func = bound_method.__func__ if six.PY3 else bound_method.im_func
        raise NotImplementedError('%s method is not transition' % func.__name__)
    meta = bound_method._sa_fsm
    instance = bound_method.__self__ if six.PY3 else bound_method.im_self
    return meta.has_transition(instance) and meta.conditions_met(instance, *args, **kwargs)
