#!/usr/bin/python env
# -*- coding: utf-8 -*-
__author__ = 'Huang yi'

class Utility(object):
    def __init__(self):
        pass

    def CheckSame(self, input1, input2):
        file1 = open(input1)
        file2 = open(input2)
        f1 = [] 
        f2 = [] 
        both_list = []

        file1.readline()
        for line in file1:
            f1.append(line.rstrip())

        file2.readline()
        for line in file2:
            f2.append(line.rstrip())

        for e in f1:
            if e in f2:
                both_list.append(e)

        print '相同元素：'
        print both_list
        print '相同个数：'
        print len(both_list)
        file1.close()
        file2.close()

if __name__ == '__main__':
    tool = Utility()
    tool.CheckSame('file3.txt', 'file2.txt')

