## dlaCreateProject.py - take a list of 2 datasets and export a Configuration file
## December 2015
## Loop through the source and target datasets and write an xml document

import os, sys, traceback, time, xml.dom.minidom, arcpy
from xml.dom.minidom import Document
import re

# Local variables...
debug = False
# Parameters
sourceDataset = arcpy.GetParameterAsText(0) # source dataset to analyze
targetDataset = arcpy.GetParameterAsText(1) # target dataset to analyze
xmlFileName = arcpy.GetParameterAsText(2) # output file name argument

if not xmlFileName.lower().endswith(".xml"):
    xmlFileName = xmlFileName + ".xml"
successParameterNumber = 3
xmlStr = ""

def main(argv = None):
    global sourceDataset,targetDataset,xmlFileName   
    createDlaFile(sourceDataset,targetDataset,xmlFileName)

def createDlaFile(sourceDataset,targetDataset,xmlFileName):

    #success = False
    writeDocument(sourceDataset,targetDataset,xmlFileName)
    #if xmlStrSource != "":
    #    success = True
    #arcpy.SetParameter(successParameterNumber, success)
    #arcpy.ResetProgressor()

    return True

def writeDocument(sourceDataset,targetDataset,xmlFileName):
    desc = arcpy.Describe(sourceDataset)
    descT = arcpy.Describe(targetDataset)

    arcpy.AddMessage(sourceDataset)
    xmlDoc = Document()
    root = xmlDoc.createElement('SourceTargetMatrix')
    xmlDoc.appendChild(root)
    root.setAttribute("version",'1.1')
    root.setAttribute("xmlns:esri",'http://www.esri.com')

    setSourceTarget(root,xmlDoc,"Source",sourceDataset)
    setSourceTarget(root,xmlDoc,"Target",targetDataset)
    
    dataset = xmlDoc.createElement("Dataset")
    root.appendChild(dataset)

    fields = getFields(descT,targetDataset)
    sourceFields = getFields(desc,sourceDataset)
    sourceNames = [field.name[field.name.rfind(".")+1:] for field in sourceFields]
    #try:
    for field in fields:
        fNode = xmlDoc.createElement("Field")
        dataset.appendChild(fNode)
        fieldName = field.name[field.name.rfind(".")+1:]
        method = 'None'
        if fieldName in sourceNames:
            addFieldElement(xmlDoc,fNode,"SourceName",fieldName)
            method = 'Copy'
        else:
            addFieldElement(xmlDoc,fNode,"SourceName","")#"*"+fieldName+"*") magic needed here...

        addFieldElement(xmlDoc,fNode,"TargetName",fieldName)
        addFieldElement(xmlDoc,fNode,"Method",method)

    # write the source field values
    setSourceFields(root,xmlDoc,dataset,sourceFields)
    # Should add a template section for value maps, maybe write domains...
    # could try to preset field mapping and domain mapping...

    # write it out
    xmlStr = xmlDoc.toprettyxml()
    xmlDoc.writexml( open(xmlFileName, 'w'),indent="  ",addindent="  ",newl='\n')
    xmlDoc.unlink()

    #except:
    #showTraceback()
    #    xmlStr =""
    


def setSourceTarget(root,xmlDoc,name,dataset):
    # set source and target elements
    sourcetarget = xmlDoc.createElement(name)
    nodeText = xmlDoc.createTextNode(dataset)
    sourcetarget.appendChild(nodeText)
    root.appendChild(sourcetarget)
    
def getName(desc,dataset):
    # get the name without prefix but maybe suffix
    if desc.baseName.find('.') > -1:
        baseName = desc.baseName[desc.baseName.rfind('.')+1:]
    else:
        baseName = desc.baseName
    if desc.dataElementType == "DEShapeFile":
        baseName = baseName + ".shp"
    return baseName

def setSourceFields(root,xmlDoc,dataset,fields):
    # Set SourceFields section of document
    sourceFields = xmlDoc.createElement("SourceFields")
    
    for field in fields:
        fNode = xmlDoc.createElement("SourceField")
        sourceFields.appendChild(fNode)
        fieldName = field.name[field.name.rfind(".")+1:]
        addFieldElement(xmlDoc,fNode,"Name",fieldName)
        addFieldElement(xmlDoc,fNode,"Type",field.type)
        if field.length != None:
            addFieldElement(xmlDoc,fNode,"Length",str(field.length))

    root.appendChild(sourceFields)

def addFieldElement(xmlDoc,node,name,value):
    xmlName = xmlDoc.createElement(name)
    node.appendChild(xmlName)
    nodeText = xmlDoc.createTextNode(value)
    xmlName.appendChild(nodeText)

def getFields(desc,dataset):
    fields = []
    ignore = []
    for name in ["OIDFieldName","ShapeFieldName","LengthFieldName","AreaFieldName"]:
        val = getFieldExcept(desc,name)
        if val != None:
            val = val[val.rfind(".")+1:]
            ignore.append(val)
    for field in arcpy.ListFields(dataset):
        if field.name[field.name.rfind(".")+1:] not in ignore:
            fields.append(field)

    return fields

def getFieldExcept(desc,name):
    val = None
    try:
        val = eval("desc." + name)
    except:
        val = None
    return val

if __name__ == "__main__":
    main()