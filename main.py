import unittest
from test_GoogleSearchCode import Test as GoogleSearch
from test_BookmarkStar import Test as Bookmark
from test_NewTab import Test as Tab
from test_Youtube import Test as Yt
from test_Amazon import Test as Amazon
from test_Twitch import Test as Twitch
from test_PdfFormInput import Test as Pdf

# Get all the test cases
google_search = unittest.TestLoader().loadTestsFromTestCase(GoogleSearch)
bookmark = unittest.TestLoader().loadTestsFromTestCase(Bookmark)
new_tab = unittest.TestLoader().loadTestsFromTestCase(Tab)
youtube = unittest.TestLoader().loadTestsFromTestCase(Yt)
amazon = unittest.TestLoader().loadTestsFromTestCase(Amazon)
twitch = unittest.TestLoader().loadTestsFromTestCase(Twitch)
pdf_form = unittest.TestLoader().loadTestsFromTestCase(Pdf)

# create a test suite combining all the test case
test_suite = unittest.TestSuite([google_search, bookmark, new_tab, youtube, amazon, twitch, pdf_form])

# Press the green button in the gutter to run the smoke test suite.
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite)
