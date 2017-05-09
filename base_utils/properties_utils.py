# coding=utf-8

import ConfigParser

__author__ = 'sinlov'


class PrettyConfigParser(ConfigParser.ConfigParser):
    def optionxform(self, option):
        return option


cf = PrettyConfigParser()
cf.read('test.properties')

section = cf.sections()
print 'section: ', section

opt = cf.options('dynamic')
print 'option: ', opt

mainAct = cf.get('dynamic', 'mainActivity')
print 'mainAct: ', mainAct

cf.set('dynamic', 'mainActivity', 'demo.MainActivity')
file_io = open('test.properties', 'w')
cf.write(file_io)
file_io.close()
