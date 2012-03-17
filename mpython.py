#!/usr/bin/python

from ast import *

def name(x, ctx):
  return Name(id=x, ctx = ctx, lineno=0, col_offset=0)

def call(f, args):
  f = name(f, Load())
  return Call(func = f, args=args, lineno=0, col_offset=0, keywords=[], vararg=None)

def func(args, body):
  return Lambda(args = arguments(args = args, defaults = []), body = body, vararg=None, lineno=0, col_offset=0)

unit = Tuple(elts = [],lineno=0,col_offset=0,ctx=Load())

def transform(elt, generators):
  if len(generators) ==1:
    var = generators[0].target
    var = name(var.id, Param())

    m = generators[0].iter
    ifs = generators[0].ifs
    elt = call("singleton", [elt])
    for i in ifs[-1::-1]:
      ifexp = IfExp(i,
                    call('singleton',[unit]),
                    call('fail', []), lineno=0, col_offset=0)
      lambdaFunction = func([name('_', Param())], elt)
      elt = call("concatMap", [lambdaFunction, ifexp])
    lambdaFunction = func([var], elt)
    return call("concatMap", [lambdaFunction, m])
  else:
    var = generators[0].target
    var = name(var.id, Param())

    m = generators[0].iter
    ifs = generators[0].ifs
    elt = transform(elt, generators[1:])
    for i in ifs[-1::-1]:
      ifexp = IfExp(i,
                    call('singleton',[unit]),
                    call('fail', []), lineno=0, col_offset=0)
      lambdaFunction = func([name('_', Param())], elt)
      elt = call("concatMap", [lambdaFunction, ifexp])
    lambdaFunction = func([var], elt)
    return call("concatMap", [lambdaFunction, m])

class RewriteComp(NodeTransformer):
  def visit_ListComp(self, node):
    newNode = node
    elt = node.elt
    generators = node.generators

    elt = RewriteComp().visit(elt)
    generators = map(RewriteComp().visit,generators)

    newNode = transform(elt, generators)
    return newNode

def concatMap(f, x):
  return [z for y in x for z in f(y)]

def singleton(x):
  return [x]

def fail():
  return []

#print concatMap(singleton, [1,2,3])

#print concatMap(lambda x:singleton(10*x), [1,2,3])

import sys
source = open(sys.argv[1]).read()
e = compile(source, "<string>", "exec", PyCF_ONLY_AST)
e = RewriteComp().visit(e)
f = compile(e, "<string>", "exec")
print f
exec f
print "Done"