Finite state machine field for plain old python objects (POPOs) (based on sqlalchemy-fsm)
==============================================================

popo-fsm adds declarative states management for plain old python objects (POPO).
Instead of adding some state field to a POPO, and managing its
values by hand, you could use a plain old python field and mark POPO methods
with the `transition` decorator. Your method will contain the side-effects
of the state change.

The decorator also takes a list of conditions, all of which must be met
before a transition is allowed.

Usage
-----

Add a plain old python field to you POPO
    from popo_fsm import transition

    class BlogPost(object):
        def __init__():
            self.state = 'new'


Use the `transition` decorator to annotate POPO methods

    @transition('state', source='new', target='published')
    def publish(self):
        """
        This function may contain side-effects, 
        like updating caches, notifying users, etc.
        The return value will be discarded.
        """

`source` parameter accepts a list of states, or an individual state.
You can use `*` for source, to allow switching to `target` from any state.

If calling publish() succeeds without raising an exception, the state field
will be changed.

    from popo_fsm import can_proceed

    def publish_view(request, post_id):
        post = get_object__or_404(BlogPost, pk=post_id)
        if not can_proceed(post.publish):
             raise Http404;

        post.publish()
        post.save()
        return redirect('/')


If your given function requires arguments to validate, you need to include them
when calling can_proceed as well as including them when you call the function
normally. Say publish() required a date for some reason:

    if not can_proceed(post.publish, the_date):
        raise Http404
    else:
        post.publish(the_date)

If you require some conditions to be met before changing state, use the
`conditions` argument to `transition`. `conditions` must be a list of functions
that take one argument, the POPO instance.  The function must return either
`True` or `False` or a value that evaluates to `True` or `False`. If all
functions return `True`, all conditions are considered to be met and transition
is allowed to happen. If one of the functions return `False`, the transition
will not happen. These functions should not have any side effects.

You can use ordinary functions

    def can_publish(instance):
        # No publishing after 17 hours
        if datetime.datetime.now().hour > 17:
           return False
        return True

Or POPO methods

    def can_destroy(self):
        return self.is_under_investigation()

Use the conditions like this:

    @transition('state', source='new', target='published', conditions=[can_publish])
    def publish(self):
        """
        Side effects galore
        """

    @transition('state', source='*', target='destroyed', conditions=[can_destroy])
    def destroy(self):
        """
        Side effects galore
        """


How does popo-fsm diverge from sqlalchemy-fsm?
------------------------------------------------

* Works with POPOs, doesn't depend on sqlalchemy

* Has no special support for sqlalchemy

* Supports multiple state fields in a single object
