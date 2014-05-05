import os
import types
from sphinx.util.osutil import os_path
from jinja2 import contextfunction

from tocnode import TocNode


class EclipseTocNode(TocNode):
    """
    Sphinx ToC with ability to be rendered in eclpise help ToC
    """

    def render(self, pathto):
        if not self.children:
            return u'<topic label="%s" href="%s" />' % (self.text, self.link)

        out = [u'<%s label="%s" href="%s">' % (
            'topic' if self.parent else 'toc', self.text, self.link)]
        for item in self.children:
            text = '\t' + item.render(pathto).replace('\n', '\n\t')
            out.append(text)
        out.append('</%s>' % ('topic' if self.parent else 'toc'))
        return u'\n'.join(out)


def handler(app):
    builder = app.builder

    @contextfunction
    def eclipsetoc(ctx):
        pathto = ctx['pathto']
        root = EclipseTocNode.build(builder, page=builder.config.master_doc)[0]
        return root.render(pathto=pathto)

    # patch builder to generate .xml extension file
    old_get_outfilename = builder.get_outfilename

    def get_outfilename(self, pagename):
        if pagename == 'toc.xml':
            return os.path.join(self.outdir, os_path(pagename))
        return old_get_outfilename(pagename)

    builder.get_outfilename = types.MethodType(get_outfilename, builder, type(builder))

    return [('toc.xml', {'eclipsetoc': eclipsetoc}, 'toc.xml')]


def setup(app):
    app.connect('html-collect-pages', handler)
