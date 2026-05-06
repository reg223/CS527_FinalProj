import pytest
import mechanicalsoup
from mechanicalsoup import Browser, Form, InvalidFormMethod, LinkNotFoundError
from http.cookiejar import CookieJar
from bs4 import BeautifulSoup

@pytest.fixture
def browser():
    return Browser()

def test_browser_initialization(browser):
    assert isinstance(browser, mechanicalsoup.Browser)

def test_set_user_agent(browser):
    browser.set_user_agent("TestAgent/1.0")
    assert browser.session.headers['User-Agent'] == "TestAgent/1.0"

def test_set_cookiejar(browser):
    cookiejar = CookieJar()
    browser.set_cookiejar(cookiejar)
    assert browser.get_cookiejar() == cookiejar

def test_add_soup_with_html_response(browser):
    class MockResponse:
        def __init__(self, content, headers):
            self.content = content
            self.headers = headers
            self.text = content.decode('utf-8')
            self.encoding = 'utf-8'
    
    response = MockResponse(b"<html><body></body></html>", {"Content-Type": "text/html"})
    browser.add_soup(response, {})
    assert response.soup is not None

def test_add_soup_with_non_html_response(browser):
    class MockResponse:
        def __init__(self, content, headers):
            self.content = content
            self.headers = headers
            self.text = content.decode('utf-8')
            self.encoding = 'utf-8'
    
    response = MockResponse(b"Not HTML content", {"Content-Type": "text/plain"})
    browser.add_soup(response, {})
    assert response.soup is None

def test_form_initialization():
    html = '<form><input name="username" type="text"></form>'
    soup = BeautifulSoup(html, 'html.parser')
    form = Form(soup.find('form'))
    assert form.form.name == 'form'

def test_form_set_input():
    html = '<form><input name="username" type="text"></form>'
    soup = BeautifulSoup(html, 'html.parser')
    form = Form(soup.find('form'))
    form.set_input({"username": "test_user"})
    assert form.form.find("input", {"name": "username"})["value"] == "test_user"

def test_form_set_input_invalid_field():
    html = '<form><input name="username" type="text"></form>'
    soup = BeautifulSoup(html, 'html.parser')
    form = Form(soup.find('form'))
    with pytest.raises(InvalidFormMethod):
        form.set_input({"password": "test_pass"})

def test_form_set_checkbox():
    html = '<form><input name="agree" type="checkbox"></form>'
    soup = BeautifulSoup(html, 'html.parser')
    form = Form(soup.find('form'))
    form.set_checkbox({"agree": True})
    assert form.form.find("input", {"name": "agree"})["checked"] == ""

def test_form_set_radio():
    html = '<form><input name="gender" type="radio" value="male"><input name="gender" type="radio" value="female"></form>'
    soup = BeautifulSoup(html, 'html.parser')
    form = Form(soup.find('form'))
    form.set_radio({"gender": "female"})
    assert form.form.find("input", {"name": "gender", "value": "female"})["checked"] == ""

def test_form_set_textarea():
    html = '<form><textarea name="comments"></textarea></form>'
    soup = BeautifulSoup(html, 'html.parser')
    form = Form(soup.find('form'))
    form.set_textarea({"comments": "This is a comment."})
    assert form.form.find("textarea", {"name": "comments"}).string == "This is a comment."

def test_form_set_select():
    html = '<form><select name="options"><option value="1">One</option><option value="2">Two</option></select></form>'
    soup = BeautifulSoup(html, 'html.parser')
    form = Form(soup.find('form'))
    form.set_select({"options": "2"})
    assert form.form.find("select", {"name": "options"}).find("option", {"value": "2"})["selected"] == "selected"

def test_invalid_form_method_exception():
    html = '<form></form>'
    soup = BeautifulSoup(html, 'html.parser')
    form = Form(soup.find('form'))
    with pytest.raises(LinkNotFoundError):
        form.set_checkbox({"nonexistent": True})
