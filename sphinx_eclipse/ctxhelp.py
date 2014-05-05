import os
import warnings
import types
from docutils import nodes
from sphinx.util.compat import Directive, make_admonition
from sphinx.util.osutil import os_path


class CtxHelpNode(nodes.General, nodes.Element):
    pass


def visit_CtxHelpNode(self, node):
    self.visit_admonition(node)


def depart_CtxHelpNode(self, node):
    self.depart_admonition(node)


class CtxHelpDirective(Directive):
    has_content = True
    required_arguments = 1
    option_spec = {
        'ref': str,
    }

    def run(self):
        env = self.state.document.settings.env
        ref = self.options.get('ref') or self.state.document.settings.env.docname
        context_id = self.arguments[0]
        description = u'\n'.join(self.content.data)

        if not hasattr(env, '_eclipse_ctx_help'):
            env._eclipse_ctx_help = {}
        env._eclipse_ctx_help.setdefault(context_id, {'topics': []})
        ctx = env._eclipse_ctx_help[context_id]

        ctx['topics'].append(ref)
        
        if description and ctx.get('description'):
            if description == ctx['description']:
                warnings.warn(u'Directive eclipse_ctx_help in %s:%s has duplicate description' % (
                    self.state.document.settings.env.docname, self.lineno))
            else:
                raise Exception(u'Directive eclipse_ctx_help in %s:%s has redefined description' % (
                    self.state.document.settings.env.docname, self.lineno))
        else:
            ctx['description'] = description
        return []


def get_outfilename(self, pagename):
    if pagename in self.config.html_additional_pages:
        return os.path.join(self.outdir, os_path(self.config.html_additional_pages[pagename]))
    return os.path.join(self.outdir, os_path(pagename) + self.out_suffix)


def handler(app):
    builder = app.builder

    def eclipse_context_help():
        out = []

        domain = app.env.domains['std']
        refs = domain.data['anonlabels']

        for context_id, ctx in app.env._eclipse_ctx_help.iteritems():
            out.append('\t<context id="%s">' % context_id)
            if ctx.get('description'):
                out.append('\t\t<description>%s</description>' % ctx['description'])
            for topic in ctx['topics']:
                if topic in app.env.titles:
                    anchor = ''
                    docname = topic
                    title = app.env.titles[docname].astext()
                elif topic in refs:
                    ref = refs[topic]
                    docname = ref[0]
                    anchor = ref[1]
                    if len(ref) > 2:
                        title = ref[2]
                    else:
                        title = app.env.titles[docname].astext()
                else:
                    raise Exception(u'Reference %s not found as label or page.' % topic)

                out.append('\t\t<topic href="%s#%s" label="%s" />' % (
                    os.path.join(builder.config['eclipse_base_path'],
                                 builder.get_target_uri(docname)),
                    anchor,
                    title,
                ))
            out.append('\t</context>')
        return u'\n'.join(out)

    # patch builder to generate .xml extension file
    old_get_outfilename = builder.get_outfilename

    def get_outfilename(self, pagename):
        if pagename == 'context.xml':
            return os.path.join(self.outdir, os_path(pagename))
        return old_get_outfilename(pagename)

    builder.get_outfilename = types.MethodType(get_outfilename, builder, type(builder))
    
    return [('context.xml', {'eclipse_context_help': eclipse_context_help}, 'context.xml')]


def purge_handler(app, env, docname):
    try:
        app.env._eclipse_ctx_help
    except AttributeError:
        pass  # empty
    else:
        for context_id, ctx in app.env._eclipse_ctx_help.iteritems():
            if docname in ctx['topics']:
                ctx['topics'].remove(docname)


def setup(app):
    app.add_node(CtxHelpNode,
                 html=(visit_CtxHelpNode, depart_CtxHelpNode),
                 latex=(visit_CtxHelpNode, depart_CtxHelpNode),
                 text=(visit_CtxHelpNode, depart_CtxHelpNode))
    app.add_directive('eclipse_ctx_help', CtxHelpDirective)
    app.connect('html-collect-pages', handler)
    app.connect('env-purge-doc', purge_handler)
