import os
from docutils import nodes
from sphinx.addnodes import toctree


class TocNode(object):
    """
    Sphinx toctree simplified representation
    """
    __slots__ = ('key', 'link', 'text', 'children', 'parent')

    def __init__(self, key, link, text, children=None, parent=None):
        self.key = key
        self.link = link
        self.text = text
        self.children = []
        self.parent = parent
        if children:
            self.add_children(children)

    def __repr__(self):
        return u'<%s %s %s>' % (self.__class__.__name__, self.link, self.text)

    def add_children(self, children):
        for item in children:
            item.parent = self
        self.children.extend(children)
    
    @classmethod
    def build(cls, builder, page=None):
        """
        Builds navigation from toctree data.
        
        Warning! Strong sphinx magic ahead: watch out for indexes.
        """
    
        node = builder.env.tocs[page]
    
        items = []
        if len(node[0]) > 1:  # no children
            for item in node[0][1].children:
                if isinstance(item, toctree):
                    for i, subpage in item['entries']:
                        items.extend(cls.build(builder, page=subpage))
                elif isinstance(item, nodes.list_item):
                    items.append(cls(
                        item[0][0]['refuri'],
                        link=os.path.join(builder.config['eclipse_base_path'],
                                          builder.get_target_uri(item[0][0]['refuri']) + item[0][0]['anchorname']),
                        text=item[0][0].astext()
                    ))
                else:
                    raise Warning(u'Unknown element %s in toc' % repr(item))
    
        if len(node[0]) > 0:
            ref = node[0][0][0]
            return [cls(
                key=ref['refuri'],
                link=os.path.join(builder.config['eclipse_base_path'],
                                  builder.get_target_uri(ref['refuri']) + ref['anchorname']),
                text=ref.astext(),
                children=items
            )]
        else:
            return items

