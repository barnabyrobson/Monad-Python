#!/usr/bin/python

import ast
import sys


def name(x, ctx):
    return ast.Name(id=x, ctx=ctx, lineno=0, col_offset=0)


def call(f, *args):
    f = name(f, ast.Load())
    return ast.Call(func=f, args=list(args), lineno=0,
                    col_offset=0, keywords=[], vararg=None)


def func(args, body):
    return ast.Lambda(args=ast.arguments(args=args, defaults=[]),
                      body=body, vararg=None, lineno=0, col_offset=0)


unit = ast.Tuple(elts=[], lineno=0, col_offset=0, ctx=ast.Load())


def transform(elt, generators):
    elt = call("__singleton__", elt)

    for generator in generators[-1::-1]:
        for i in generator.ifs[-1::-1]:
            elt = call("__concatMap__",
                       func([name('_', ast.Param())], elt),
                       ast.IfExp(i,
                                 call('__singleton__', unit),
                                 call('__fail__'), lineno=0, col_offset=0))

        elt = call("__concatMap__",
                   func([name(generator.target.id, ast.Param())], elt),
                   generator.iter)
    return elt


class RewriteComp(ast.NodeTransformer):
    def visit_ListComp(self, node):
        return transform(RewriteComp().visit(node.elt),
                         [RewriteComp().visit(generator)
                         for generator in node.generators])


def __concatMap__(f, x):
    return [z for y in x for z in f(y)]


def __singleton__(x):
    return [x]


def __fail__():
    return []


source = open(sys.argv[1]).read()
e = compile(source, "<string>", "exec", ast.PyCF_ONLY_AST)
e = RewriteComp().visit(e)
f = compile(e, sys.argv[1], "exec")
print f
exec f
print "Done"
