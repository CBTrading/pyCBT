from unittest import TestCase

import pyCBT.common.timezone as timezone

class TestTimeShift(TestCase):
    def test_is_timezone(self):
        dt = timezone.datetime.now(tzinfo=timezone.pytz.timezone("America/Caracas"))
        self.assertTrue(bool(dt.tzinfo))
