import maya.cmds as cmds
import json
import os

def importnetwork(jsoninput):
    """Taking in a json stream or file, create the network."""

    shadertypes = ['bxdf']
    texturetypes = ['pattern']
    if os.path.isfile(jsoninput):
        data = ""
        with open(jsoninput, 'r') as myfile:
            data += myfile.read().replace('\n', '')
    else:
        data=jsoninput
    data = json.loads(data)
    print data
    #Create Nodes needed
    nodelist = []
    for nodename, nodedata in data.iteritems():
        x = None
        if nodedata['TYPE'] in shadertypes:
            x = cmds.shadingNode(nodedata['STYLE'], name=nodename, asShader=True)
        elif nodedata['TYPE'] in texturetypes:
            x = cmds.shadingNode(nodedata['STYLE'], name=nodename, asTexture=True)
        
        if x:
            if str(x) not in nodename:
                data[nodename]['name'] = str(x)
            nodelist.append(x)
    
    #Change Attrs
    print len(nodelist), 'Nodes made.'
    for node in nodelist:
        # Get the node key
        key = _getConnectedNode(data, node)
        
        if key: 
            print "---------------------------------------------------"       
            print "Key is:", key
           
            for destattr in cmds.listAttr(node):
                if destattr in data[key]['ATTRIBUTES'].keys():
                    print "Attr found"
                    if type(data[key]['ATTRIBUTES'][destattr]) is list:
                        if "connection" in str(data[key]['ATTRIBUTES'][destattr][0]):
                            print 'CONNECTION!'
                            srcnode = str(data[key]['ATTRIBUTES'][destattr][1])
                            srcattr = str(data[key]['ATTRIBUTES'][destattr][2])
                            if srcnode not in nodelist:
                                for n, d in data.iteritems():
                                    if 'name' in d.keys() and srcnode == n:
                                        srcnode=d['name']
                            cmds.connectAttr('%s.%s' % (srcnode, srcattr),
                                             '%s.%s' % (node, destattr))
                                         
                        else:
                            cmds.setAttr('%s.%s' % (node, destattr),
                                         float(data[key]['ATTRIBUTES'][destattr][0]),
                                         float(data[key]['ATTRIBUTES'][destattr][1]),
                                         float(data[key]['ATTRIBUTES'][destattr][2]))
                    else:
                        attrtype = cmds.getAttr('%s.%s' % (node, destattr), type=True)
                        if 'float' in str(attrtype):
                            cmds.setAttr('%s.%s' % (node, destattr),
                                         float(data[key]['ATTRIBUTES'][destattr]))
                        elif 'int' in str(attrtype):
                            cmds.setAttr('%s.%s' % (node, destattr),
                                         int(data[key]['ATTRIBUTES'][destattr]))
                        elif 'string' in str(attrtype):
                            cmds.setAttr('%s.%s' % (node, destattr),
                                         str(data[key]['ATTRIBUTES'][destattr]))


        else:
            print "Node not found!!!!"

def _getConnectedNode(data, node):
    """Return the node that matches."""
    if str(node) in data.keys():
        return str(node)
    else:
        for nodekey, nodedata in data.iteritems():
            if 'name' in nodedata.keys():
                if nodedata['name'] == str(node):
                    return nodekey
    return None

importnetwork(os.path.join('G:\\', 'Dropbox', 'OSE', 'simpletest.json')) 