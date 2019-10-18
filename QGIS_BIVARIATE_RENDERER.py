
#//QGIS BIVARIATE RENDERER OCTOBER 2019 Mitchell Younes RMIT//

# Welcome to my custom QGIS bivariate renderer.
# This script will allow you to create a bivariate choropleth.
# Some notes about using the script:
#   - This script has been designed to be deployed from the QGIS Processing Script Editor
#   - This script has been specifically designed for shapefiles with polygon features.
#   - Moreover, the respective polgons will be used as enumeration units.
#   - Also, you will need to specify two fields that you wish to analyse.
#   - For these fields, remember to use derived data such as normalised data or rates.
#   - Apart from that, enjoy!

from qgis.core import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.utils import iface
import numpy as np


# Please set your input data below:
#   - filepath: Should be the folder where your shapefile is located.
#   - base: The filename of your shapefile. The file used in this example has been provided under the same name.
#   - output: This will be the name of the choropleth instance which will be added to your display.
#   - xVar: Your X variable.
#   - yVar: Your Y variable.


filepath = "/Users/mitchellbwyounes/Documents/Study/MC265/YEAR2/GISPRO/PROJECT/FILES/"
base = "bivarinput.shp"
output = "bivaroutput"
xVar = "AVFIRE"
yVar = "POPDEN"

# Input file is being converted to QGIS format and bivariate class variables are added if necessary.    
#   - In this section, three fields will be added to your file, xClass, yClass.
#   - These fields will hold a value which will be later used to determine which colour value to set to each polygon.
#   - This section also checks if these fields already exist in yout file. Just in case, you wanted to repeat this process.

baseLayer = QgsVectorLayer((filepath + base), base[:-4],"ogr")
provider = baseLayer.dataProvider()
baseLayer.startEditing()
if baseLayer.fields().lookupField("xClass") is -1:
    provider.addAttributes([QgsField("xClass", QVariant.String)])
if baseLayer.fields().lookupField("yClass") is -1:
    provider.addAttributes([QgsField("yClass", QVariant.String)])
if baseLayer.fields().lookupField("BivarClass") is -1:
    provider.addAttributes([QgsField("BivarClass", QVariant.String)])
baseLayer.updateFields()
baseLayer.commitChanges()

# Equal Interval breaks are determined.
#   - In this section, equal interval break values are determined for both the Y and X varible.

xLocator = baseLayer.fields().lookupField(xVar)
yLocator = baseLayer.fields().lookupField(yVar)
xList = []
yList = []
baseFeat = baseLayer.getFeatures()
for feat in baseFeat:
    attrs = feat.attributes()
    xList.append(attrs[xLocator])
    yList. append(attrs[yLocator])
xField = np.array(xList)
yField = np.array(yList)
xPer1 = np.percentile(xField, 25)
xPer2 = np.percentile(xField, 50) 
xPer3 = np.percentile(xField, 75)
yPer1 = np.percentile(yField, 25)
yPer2 = np.percentile(yField, 50) 
yPer3 = np.percentile(yField, 75)

# For both X and Y variables, every record is classed depending on the previously determined breakpoints.

baseFeat = baseLayer.getFeatures()
for feat in baseFeat:
    if feat[xVar] < xPer1:
        xClass = 1
    elif xPer1 < feat[xVar] < xPer2:
        xClass = 2
    elif xPer2 < feat[xVar] < xPer3:
        xClass = 3
    elif xPer3 < feat[xVar]:
        xClass = 4
    if feat[yVar] < yPer1:
        yClass = 1
    elif yPer1 < feat[yVar] < yPer2:
        yClass = 2
    elif yPer2 < feat[yVar] < yPer3:
        yClass = 3
    elif yPer3 < feat[yVar]:
        yClass = 4
    baseLayer.startEditing()
    feat["xClass"] = xClass
    feat["yClass"] = yClass
    baseLayer.updateFeature(feat)
baseLayer.commitChanges()

# For every record, the newly created X and Y classes are concatenated to produce the bivariate class.
#   - The bivariate class will hold a unique combination of digits ranging from '11' to '44'.

baseFeat = baseLayer.getFeatures()
for feat in baseFeat:
    baseLayer.startEditing()
    feat["BivarClass"] = str(feat["yClass"]) + str(feat["xClass"])
    baseLayer.updateFeature(feat)
baseLayer.commitChanges()

# The bivariate class is used to determine the relevant colour value of each record, in this case a polygon feature.
#   - To better understand how this bivariate colour ramp works, please see the 'BIVARIATE_COLOUR_RAMP' image file.
#   - Each polygon is then rendered to its respective colour value.

renderLayer = iface.addVectorLayer((filepath + base), base[:-4],"ogr")

bivarValue = {"11":(QColor(243,243,243), None),"12":(QColor(235, 179, 166), None), 
"13":(QColor(229, 119, 94), None), "14":(QColor(226, 68, 49), None), 
"21":(QColor(182, 204, 235), None), "22":(QColor(166, 142, 151), None),
"23":(QColor(161, 92, 81), None),"24":(QColor(158, 49, 31), None), 
"31":(QColor(122, 167, 227), None), "32":(QColor(109, 115, 145), None), 
"33":(QColor(104, 72, 75), None), "34":(QColor(101, 34, 17), None), 
"41":(QColor(62, 130, 220), None), "42":(QColor(53, 88, 140), None), 
"43":(QColor(48, 54, 71), None), "44":(QColor(45, 21, 4), None)}
categories= []
for val, (colour, label) in bivarValue.items():
    sym = QgsSymbol.defaultSymbol(renderLayer.geometryType())
    sym.setColor(colour)
    category = QgsRendererCategory(val, sym, label)
    categories.append(category)
    
# Lastly, the newly rendered layer is added to the display.
    
field = "BivarClass"

renderFields = QgsCategorizedSymbolRenderer(field, categories)

renderLayer.setRenderer(renderFields)

for layer in iface.layerTreeView().selectedLayers():
    layer.setName(output)

QgsProject.instance().addMapLayer(renderLayer)

# Thank you for using this bivariate renderer!
