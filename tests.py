import unittest
from popo_fsm import transition, can_proceed, TransitionNotAllowed


class BlogPost(object):
    def __init__(self, **kwargs):
        self.state = 'new'
        super(BlogPost, self).__init__(**kwargs)

    @transition('state', source='new', target='published')
    def publish(self):
        pass

    @transition('state', source='published', target='hidden')
    def hide(self):
        pass

    @transition('state', source='new', target='removed')
    def remove(self):
        raise Exception('No rights to delete %s' % self)

    @transition('state', source=['published', 'hidden'], target='stolen')
    def steal(self):
        pass

    @transition('state', source='*', target='moderated')
    def moderate(self):
        pass


class FSMFieldTest(unittest.TestCase):
    def setUp(self):
        self.model = BlogPost()

    def test_initial_state_instantiated(self):
        self.assertEqual(self.model.state, 'new')

    def test_known_transition_should_succeed(self):
        self.assertTrue(can_proceed(self.model.publish))
        self.model.publish()
        self.assertEqual(self.model.state, 'published')

        self.assertTrue(can_proceed(self.model.hide))
        self.model.hide()
        self.assertEqual(self.model.state, 'hidden')

    def test_unknown_transition_fails(self):
        self.assertFalse(can_proceed(self.model.hide))
        self.assertRaises(TransitionNotAllowed, self.model.hide)

    def test_state_non_changed_after_fail(self):
        self.assertRaises(Exception, self.model.remove)
        self.assertTrue(can_proceed(self.model.remove))
        self.assertEqual(self.model.state, 'new')

    def test_multiple_source_support_path_1_works(self):
        self.model.publish()
        self.model.steal()
        self.assertEqual(self.model.state, 'stolen')

    def test_multiple_source_support_path_2_works(self):
        self.model.publish()
        self.model.hide()
        self.model.steal()
        self.assertEqual(self.model.state, 'stolen')

    def test_star_shortcut_succeed(self):
        self.assertTrue(can_proceed(self.model.moderate))
        self.model.moderate()
        self.assertEqual(self.model.state, 'moderated')


class MultiStateModel(object):
    def __init__(self, **kwargs):
        self.state = 'new'
        self.action = 'no'
        super(MultiStateModel, self).__init__(**kwargs)

    @transition('state', source='new', target='no')
    def change_state(self):
        pass

    @transition('action', source='no', target='new')
    def change_action(self):
        pass


class MultiStateModelTest(unittest.TestCase):
    def test_known_transition_should_succeed(self):
        model = MultiStateModel()
        self.assertTrue(can_proceed(model.change_state))
        model.change_state()
        self.assertEqual(model.state, 'no')

        self.assertTrue(can_proceed(model.change_action))
        model.change_action()
        self.assertEqual(model.action, 'new')


class Document(object):
    def __init__(self, **kwargs):
        self.status = 'new'
        super(Document, self).__init__(**kwargs)

    @transition('status', source='new', target='published')
    def publish(self):
        pass


class DocumentTest(unittest.TestCase):
    def test_any_state_field_name_allowed(self):
        model = Document()
        model.publish()
        self.assertEqual(model.status, 'published')


def condition_func(instance):
    return True


class BlogPostWithConditions(object):
    def __init__(self, **kwargs):
        self.state = 'new'
        super(BlogPostWithConditions, self).__init__(**kwargs)

    def model_condition(self):
        return True

    def unmet_condition(self):
        return False

    @transition('state', source='new', target='published', conditions=[condition_func, model_condition])
    def publish(self):
        pass

    @transition('state', source='published', target='destroyed', conditions=[condition_func, unmet_condition])
    def destroy(self):
        pass


class ConditionalTest(unittest.TestCase):
    def setUp(self):
        self.model = BlogPostWithConditions()

    def test_initial_state(self):
        self.assertEqual(self.model.state, 'new')

    def test_known_transition_should_succeed(self):
        self.assertTrue(can_proceed(self.model.publish))
        self.model.publish()
        self.assertEqual(self.model.state, 'published')

    def test_unmet_condition(self):
        self.model.publish()
        self.assertEqual(self.model.state, 'published')
        self.assertFalse(can_proceed(self.model.destroy))
        self.model.destroy()
        self.assertEqual(self.model.state, 'published')


if __name__ == '__main__':
    unittest.main()
