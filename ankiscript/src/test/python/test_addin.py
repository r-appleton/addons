
import sys
import unittest
import tests.mockanki
from unittest.mock import patch, call, Mock, MagicMock
from ankiscript.addin import Addin

sys.modules['anki'] = MagicMock()
sys.modules['anki.httpclient'] = MagicMock()
import anki.httpclient

class AddinTest(unittest.TestCase):

    @patch('ankiscript.addin.mw.addonManager.addonName')
    @patch('ankiscript.addin.mw.addonManager.allAddons')
    def test_addin_is_installed(self, allAddons, addonName):
        allAddons.return_value = [Mock()]
        addonName.return_value = 'testing'
        self.assertTrue(Addin('testing').isInstalled())

    @patch('ankiscript.addin.mw.addonManager.allAddons')
    def test_addin_is_not_installed(self, allAddons):
        allAddons.return_value = ''
        self.assertFalse(Addin('testing').isInstalled())

    @unittest.skip('DownloadError type not found')
    @patch('ankiscript.addin.mw.addonManager')
    @patch('anki.httpclient.HttpClient')
    @patch('ankiscript.addin.addons.download_and_install_addon')
    @patch('ankiscript.addin.askUser')
    @patch('ankiscript.addin.mw.addonManager.allAddons')
    def test_addin_install(self, allAddons, askUser, download_and_install_addon, HttpClient, addonManager):
        allAddons.return_value = ''
        askUser.return_value = True
        download_and_install_addon.return_value = ('198750399', '')
        
        addin = Addin('testing')
        addin.install('198750399', Mock())
        download_and_install_addon.assert_called_with(addonManager, HttpClient, '198750399')
        #HttpClient

    @patch('ankiscript.addin.addons.download_and_install_addon')
    @patch('ankiscript.addin.askUser')
    @patch('ankiscript.addin.mw.addonManager.allAddons')
    def test_addin_install_not_done_if_user_cancels(self, allAddons, askUser, download_and_install_addon):
        allAddons.return_value = ''
        askUser.return_value = False
        
        addin = Addin('testing')
        addin.install('198750399', Mock())
        download_and_install_addon.assert_not_called()

    @patch('ankiscript.addin.mw.addonManager.addonName')
    @patch('ankiscript.addin.mw.addonManager.allAddons')
    def test_addin_install_when_already_installed(self, allAddons, addonName):
        allAddons.return_value = [Mock()]
        addonName.return_value = 'testing'
        Addin('testing').install('198750399', Mock())
