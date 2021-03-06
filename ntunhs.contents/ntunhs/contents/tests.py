import doctest
import unittest

from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

import ntunhs.contents

OPTION_FLAGS = doctest.NORMALIZE_WHITESPACE | \
               doctest.ELLIPSIS

ptc.setupPloneSite(products=['ntunhs.contents'])


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            zcml.load_config('configure.zcml',
              ntunhs.contents)

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='ntunhs.contents',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='ntunhs.contents.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'INTEGRATION.txt',
            package='ntunhs.contents',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),

        # -*- extra stuff goes here -*-

        # Integration tests for ntunhsfooter
        ztc.ZopeDocFileSuite(
            'ntunhsfooter.txt',
            package='ntunhs.contents',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),


        # Integration tests for ntunhspage
        ztc.ZopeDocFileSuite(
            'ntunhspage.txt',
            package='ntunhs.contents',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),



        # Integration tests for ntunhsfolder
        ztc.ZopeDocFileSuite(
            'ntunhsfolder.txt',
            package='ntunhs.contents',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),


        # Integration tests for device_list
        ztc.ZopeDocFileSuite(
            'device_list.txt',
            package='ntunhs.contents',
            optionflags = OPTION_FLAGS,
            test_class=TestCase),


        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
