import collections
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

    def has_transition(self, instance):
        return self.current_state(instance) in self.transitions or '*' in self.transitions

    def conditions_met(self, instance, *args, **kwargs):
        current_state = self.current_state(instance)
        next_state = current_state in self.transitions and self.transitions[current_state] or self.transitions['*']
        return all(map(lambda f: f(instance, *args, **kwargs), self.conditions[next_state]))

    def to_next_state(self, instance):
        current_state = self.current_state(instance)
        try:
            next_state = self.transitions[current_state]
        except KeyError:
            next_state = self.transitions['*']
        setattr(instance, self.field_name, next_state)


def transition(field, source='*', target=None, conditions=()):
    def inner_transition(func):
        if not hasattr(func, '_sa_fsm'):
            setattr(func, '_sa_fsm', FSMMeta(field))
        if isinstance(source, collections.Sequence) and not isinstance(source, basestring):
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
                                           % (meta.current_state(instance), func.func_name))
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
        raise NotImplementedError('%s method is not transition' % bound_method.im_func.__name__)
    meta = bound_method._sa_fsm
    return meta.has_transition(bound_method.im_self) and meta.conditions_met(bound_method.im_self, *args, **kwargs)
