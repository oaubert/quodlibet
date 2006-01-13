from tests import TestCase, add

import util
from util import re_esc, encode, decode
from util import find_subtitle, split_album, split_title, split_value, tagsplit
from util import format_time_long as f_t_l
import os

class Tmkdir(TestCase):
    def test_exists(self):
        util.mkdir(".")

    def test_notdirectory(self):
        self.failUnlessRaises(OSError, util.mkdir, __file__)

    def test_manydeep(self):
        self.failUnless(not os.path.isdir("nonext"))
        util.mkdir("nonext/test/test2/test3")
        try:
            self.failUnless(os.path.isdir("nonext/test/test2/test3"))
        finally:
            os.rmdir("nonext/test/test2/test3")
            os.rmdir("nonext/test/test2")
            os.rmdir("nonext/test")
            os.rmdir("nonext")
add(Tmkdir)

class Tiscommand(TestCase):
    def test_ispartial(self): self.failUnless(util.iscommand("ls"))
    def test_isfull(self): self.failUnless(util.iscommand("/bin/ls"))
    def test_notpartial(self): self.failIf(util.iscommand("zzzzzzzzz"))
    def test_notfull(self): self.failIf(util.iscommand("/bin/zzzzzzzzz"))
    def test_empty(self): self.failIf(util.iscommand(""))
add(Tiscommand)

class Tmtime(TestCase):
    def test_equal(self):
        self.failUnlessEqual(util.mtime("."), os.path.getmtime("."))
    def test_bad(self):
        self.failIf(os.path.exists("/dev/doesnotexist"))
        self.failUnlessEqual(util.mtime("/dev/doesnotexist"), 0)
add(Tmtime)

class Tunexpand(TestCase):
    d = os.path.expanduser("~")

    def test_base(self):
        self.failUnlessEqual(util.unexpand(self.d), "~")
    def test_base_trailing(self):
        self.failUnlessEqual(util.unexpand(self.d + "/"), "~/")
    def test_noprefix(self):
        self.failUnlessEqual(
            util.unexpand(self.d + "foobar/"), self.d + "foobar/")
    def test_subfile(self):
        self.failUnlessEqual(
            util.unexpand(os.path.join(self.d, "la/la")), "~/la/la")
add(Tunexpand)

class StringTests(TestCase):
    def test_to(self):
        self.assertEqual(type(util.to("foo")), str)
        self.assertEqual(type(util.to(u"foo")), str)
        self.assertEqual(util.to("foo"), "foo")
        self.assertEqual(util.to(u"foo"), "foo")

    def test_rating(self):
        self.failUnlessEqual(util.format_rating(0), "")
        for i in range(0, int(1/util.RATING_PRECISION+1)):
            self.failUnlessEqual(
                i, len(util.format_rating(i * util.RATING_PRECISION)))

    def test_escape(self):
        for s in ["foo&amp;", "<&>", "&", "&amp;", "<&testing&amp;>amp;"]:
            esc = util.escape(s)
            self.failIfEqual(s, esc)
            self.failUnlessEqual(s, util.unescape(esc))
        self.failUnlessEqual(util.escape(""), "")

    def test_re_esc(self):
        self.failUnlessEqual(re_esc(""), "")
        self.failUnlessEqual(re_esc("fo o"), "fo o")
        self.failUnlessEqual(re_esc("!bar"), "\\!bar")
        self.failUnlessEqual(re_esc("*quux#argh?woo"), "\\*quux\\#argh\\?woo")

    def test_unicode(self):
        self.failUnlessEqual(decode(""), "")
        self.failUnlessEqual(decode("foo!"), "foo!")
        self.failUnlessEqual(decode("fo\xde"), u'fo\ufffd [Invalid Encoding]')
        self.failUnlessEqual(encode(u"abcde"), "abcde")

    def test_capitalize(self):
        self.failUnlessEqual(util.capitalize(""), "")
        self.failUnlessEqual(util.capitalize("aa b"), "Aa b")
        self.failUnlessEqual(util.capitalize("aa B"), "Aa B")
        self.failUnlessEqual(util.capitalize("!aa B"), "!aa B")

    def test_title(self):
        self.failUnlessEqual(util.title(""), "")
        self.failUnlessEqual(util.title("foobar"), "Foobar")
        self.failUnlessEqual(util.title("fooBar"), "FooBar")
        self.failUnlessEqual(util.title("foo bar"), "Foo Bar")
        self.failUnlessEqual(util.title("foo 1bar"), "Foo 1bar")
        self.failUnlessEqual(util.title("foo 1  bar"), "Foo 1  Bar")
        self.failUnlessEqual(util.title("2nd"), "2nd")
        self.failUnlessEqual(util.title("it's"), "It's")

    def test_split(self):
        self.failUnlessEqual(split_value("a b"), ["a b"])
        self.failUnlessEqual(split_value("a, b"), ["a", "b"])
        self.failUnlessEqual(
            split_value("a, b and c", [",", "and"]), ["a", "b", "c"])
        self.failUnlessEqual(split_value("a b", [" "]), ["a", "b"])
        self.failUnlessEqual(split_value("a b", []), ["a b"])
        val = '\xe3\x81\x82&\xe3\x81\x84'.decode('utf-8')
        self.failUnlessEqual(split_value(val), val.split("&"))

    def test_split_wordboundry(self):
        self.failUnlessEqual(split_value("Andromeda and the Band", ["and"]),
                             ["Andromeda", "the Band"])

    def test_subtitle(self):
        # these tests shouldn't be necessary; we're really only
        # interested in split_foo.
        self.failUnlessEqual(find_subtitle("foo"), ("foo", None))
        self.failUnlessEqual(find_subtitle("foo (baz)"), ("foo", "baz"))
        self.failUnlessEqual(find_subtitle("foo (baz]"), ("foo (baz]", None))
        self.failUnlessEqual(find_subtitle("foo [baz]"), ("foo", "baz"))
        self.failUnlessEqual(find_subtitle("foo ~baz~"), ("foo", "baz"))
        self.failUnlessEqual(find_subtitle(
            u"a\u301cb\u301c".encode('utf-8')), ("a", "b"))

    def test_split_title(self):
        self.failUnlessEqual(split_title("foo ~"), ("foo ~", []))
        self.failUnlessEqual(split_title("~foo "), ("~foo ", []))
        self.failUnlessEqual(split_title("~foo ~"), ("~foo ~", []))
        self.failUnlessEqual(split_title("~foo ~bar~"), ("~foo", ["bar"]))
        self.failUnlessEqual(split_title("foo (baz)"), ("foo", ["baz"]))
        self.failUnlessEqual(split_title("foo [b, c]"), ("foo", ["b", "c"]))
        self.failUnlessEqual(split_title("foo [b c]", " "), ("foo",["b", "c"]))

    def test_split_album(self):
        self.failUnlessEqual(split_album("disk 2"), ("disk 2", None))
        self.failUnlessEqual(split_album("foo disc 1/2"), ("foo", "1/2"))
        self.failUnlessEqual(
            split_album("disc foo disc"), ("disc foo disc", None))
        self.failUnlessEqual(
            split_album("disc foo disc 1"), ("disc foo", "1"))
        
        self.failUnlessEqual(split_album("foo ~disk 3~"), ("foo", "3"))
        self.failUnlessEqual(
            split_album("foo ~crazy 3~"), ("foo ~crazy 3~", None))

    def test_split_people(self):
        self.failUnlessEqual(util.split_people("foo (bar)"), ("foo", ["bar"]))
        self.failUnlessEqual(
            util.split_people("foo (with bar)"), ("foo", ["bar"]))
        self.failUnlessEqual(
            util.split_people("foo (with with bar)"), ("foo", ["with bar"]))
        self.failUnlessEqual(
            util.split_people("foo featuring bar, qx"), ("foo", ["bar", "qx"]))

    def test_size(self):
        for k, v in {
            0: "0B", 1: "1B", 1023: "1023B",
            1024: "1.00KB", 1536: "1.50KB",
            10240: "10KB", 15360: "15KB",
            1024*1024: "1.00MB", 1024*1536: "1.50MB",
            1024*10240: "10.0MB", 1024*15360: "15.0MB"
            }.items(): self.failUnlessEqual(util.format_size(k), v)

    def test_time(self):
        self.failUnlessEqual(util.parse_time("not a time"), 0)
        # check via round-tripping
        for i in range(0, 60*60*3, 137):
            self.failUnlessEqual(util.parse_time(util.format_time(i)), i)

        self.failUnlessEqual(util.format_time(-124), "-2:04")
add(StringTests)

class Ttagsplit(TestCase):
    def test_single_tag(self):
        self.failUnlessEqual(tagsplit("foo"), ["foo"])
    def test_synth_tag(self):
        self.failUnlessEqual(tagsplit("~foo"), ["~foo"])
    def test_two_tags(self):
        self.failUnlessEqual(tagsplit("foo~bar"), ["foo", "bar"])
    def test_two_prefix(self):
        self.failUnlessEqual(tagsplit("~foo~bar"), ["foo", "bar"])
    def test_synth(self):
        self.failUnlessEqual(tagsplit("~foo~~bar"), ["foo", "~bar"])
    def test_numeric(self):
        self.failUnlessEqual(tagsplit("~#bar"), ["~#bar"])
    def test_two_numeric(self):
        self.failUnlessEqual(tagsplit("~#foo~~#bar"), ["~#foo", "~#bar"])
add(Ttagsplit)

class Tformat_time_long(TestCase):
    def test_second(s):
        s.assertEquals(f_t_l(1).split(", ")[0], _("1 second"))
    def test_seconds(s):
        s.assertEquals(f_t_l(2).split(", ")[0], _("%d seconds")%2)
    def test_notminutes(s):
        s.assertEquals(f_t_l(59).split(", ")[0], _("%d seconds")%59)
    def test_minute(s):
        s.assertEquals(f_t_l(60), _("1 minute"))
    def test_minutes(s):
        s.assertEquals(f_t_l(120).split(", ")[0], _("%d minutes")%2)
    def test_nothours(s):
        s.assertEquals(f_t_l(3599).split(", ")[0], _("%d minutes")%59)
    def test_hour(s):
        s.assertEquals(f_t_l(3600), _("1 hour"))
    def test_hours(s):
        s.assertEquals(f_t_l(7200), _("%d hours")%2)
    def test_notdays(s):
        s.assertEquals(f_t_l(86399).split(", ")[0], _("%d hours")%23)
    def test_seconds_dropped(s):
        s.assertEquals(len(f_t_l(3601).split(", ")), 2)
    def test_day(s):
        s.assertEquals(f_t_l(86400), _("1 day"))
    def test_days(s):
        s.assertEquals(f_t_l(172800).split(", ")[0], _("%d days")%2)
    def test_notyears(s):
        s.assertEquals(f_t_l(31535999).split(", ")[0], _("%d days")%364)
    def test_year(s):
        s.assertEquals(f_t_l(31536000), _("1 year"))
    def test_years(s):
        s.assertEquals(f_t_l(63072000).split(", ")[0], _("%d years")%2)
    def test_drop_zero(s):
        s.assertEquals(f_t_l(3601), ", ".join([_("1 hour"), _("1 second")]))

add(Tformat_time_long)
