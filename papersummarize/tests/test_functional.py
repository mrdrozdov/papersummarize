import transaction
import unittest
import webtest


class FunctionalTests(unittest.TestCase):

    basic_login = (
        '/login?login=basic&password=basic'
        '&next=&form.submitted=Login')
    basic_wrong_login = (
        '/login?login=basic&password=incorrect'
        '&next=&form.submitted=Login')
    basic_login_no_next = (
        '/login?login=basic&password=basic'
        '&form.submitted=Login')
    editor_login = (
        '/login?login=editor&password=editor'
        '&next=&form.submitted=Login')

    @classmethod
    def setUpClass(cls):
        from papersummarize.models.meta import Base
        from papersummarize.models import (
            User,
            Paper,
            Summary,
            Tip,
            get_tm_session,
        )
        from papersummarize import main

        settings = {
            'sqlalchemy.url': 'sqlite://',
            'auth.secret': 'seekrit',
        }
        app = main({}, **settings)
        cls.testapp = webtest.TestApp(app)

        session_factory = app.registry['dbsession_factory']
        cls.engine = session_factory.kw['bind']
        Base.metadata.create_all(bind=cls.engine)

        with transaction.manager:
            dbsession = get_tm_session(session_factory, transaction.manager)

            basic = User(name='basic', role='basic')
            basic.set_password('basic')
            dbsession.add(basic)

            editor = User(name='editor', role='editor')
            editor.set_password('editor')
            dbsession.add(editor)

            paper = Paper(arxiv_id='some_id')
            dbsession.add(paper)

            other_paper_id = 'other_id'
            other_paper = Paper(arxiv_id=other_paper_id)
            dbsession.add(other_paper)

            summary = Summary(creator=editor,
                paper=other_paper,
                data='this summary is reviewed and public.')
            dbsession.add(summary)

    @classmethod
    def tearDownClass(cls):
        from papersummarize.models.meta import Base
        Base.metadata.drop_all(bind=cls.engine)

    def test_root(self):
        self.testapp.get('/', status=200)

    def test_unexisting_page(self):
        self.testapp.get('/SomePage', status=404)

    def test_successful_log_in(self):
        res = self.testapp.get(self.basic_login, status=302)
        self.assertEqual(res.location, 'http://localhost/')

    def test_successful_log_in_no_next(self):
        res = self.testapp.get(self.basic_login_no_next, status=302)
        self.assertEqual(res.location, 'http://localhost/')

    def test_failed_log_in(self):
        res = self.testapp.get(self.basic_wrong_login, status=200)
        self.assertTrue(b'login' in res.body)

    def test_logout_link_present_when_logged_in(self):
        self.testapp.get(self.basic_login, status=302)
        res = self.testapp.get('/', status=200)
        self.assertTrue(b'Logout' in res.body)

    def test_logout_link_not_present_after_logged_out(self):
        self.testapp.get(self.basic_login, status=302)
        self.testapp.get('/', status=200)
        res = self.testapp.get('/logout', status=302)
        self.assertTrue(b'Logout' not in res.body)

    def test_anonymous_user_cannot_add_summary(self):
        res = self.testapp.get('/x/some_id/add_summary', status=302).follow()
        self.assertTrue(b'Login' in res.body)

    def test_anonymous_user_cannot_edit_summary(self):
        res = self.testapp.get('/x/some_id/add_summary', status=302).follow()
        self.assertTrue(b'Login' in res.body)

    def test_anonymous_user_cannot_add_tip(self):
        res = self.testapp.get('/x/some_id/add_tip', status=302).follow()
        self.assertTrue(b'Login' in res.body)

    def test_editor_can_add_tip(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/x/some_id/add_tip', status=200)
        self.assertTrue(b'add_tip' in res.body)

    def test_editor_can_edit_summary(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/x/other_id/edit_summary', status=200)
        self.assertTrue(b'edit_summary' in res.body)

    def test_redirect_to_edit_for_existing_summary(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/x/other_id/add_summary', status=302)
        self.assertTrue(b'edit_summary' in res.body)

    def test_redirect_to_add_for_nonexistant_summary(self):
        self.testapp.get(self.editor_login, status=302)
        res = self.testapp.get('/x/some_id/edit_summary', status=302)
        self.assertTrue(b'add_summary' in res.body)
