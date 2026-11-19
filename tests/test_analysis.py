import unittest
from analyze import classify_call, PATTERNS

class BaselineTests(unittest.TestCase):
    def test_call_types(self):
        self.assertEqual(classify_call({'title':'Support Case #1','allEmails':['a@aegiscloud.com']}),'Internal')
        self.assertEqual(classify_call({'title':'URGENT: outage','allEmails':['a@customer.com']}),'Support')
        self.assertEqual(classify_call({'title':'Renewal review','allEmails':['a@customer.com']}),'External')
    def test_multiple_topics(self):
        text='SSO outage delayed the audit.'
        self.assertTrue(PATTERNS['Identity & Integrations'].search(text))
        self.assertTrue(PATTERNS['Reliability & Incidents'].search(text))
        self.assertTrue(PATTERNS['Security & Compliance'].search(text))
    def test_whole_words(self):
        self.assertFalse(PATTERNS['Security & Compliance'].search('auditory'))
if __name__=='__main__': unittest.main()
