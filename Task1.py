# For the first task Python with QGIS is preferred to automate the workflow. You need to install pandas on your device. 
# Launch QGIS and paste the following code in the python console in QGIS after modifying the folder paths and parameter of your problem


# Model Inputs
# Specify the network folder
fn1 = "C:\\Users\\Abdullah\\Desktop\\Bentley\\Programming_exercise\\programming_task_files\\sacramento_network.shp"
# Specify the restaurants folder
fn2 = "C:\\Users\\Abdullah\\Desktop\\Bentley\\Programming_exercise\\programming_task_files\\sacramento_restaurants.shp"
# Specify the folder of the CSV file output
Results1csv = "C:\\Users\\Abdullah\\Desktop\\Bentley\\Programming_exercise\\Results1.csv"
# Specify the buffer distance in degrees (for the first task)
bufferdistance_inft = 200  # in degrees equivalant to 200 feet 0.000549494173121
# Specify a temperory folder to save some temperory files for vizualization purposes
tempfolder = "C:\\Users\\Abdullah\\Desktop\\Bentley\\temp"
############################################################################################################################

# Preparing the folder of temperory files
Outfn = tempfolder +"\\buffer.shp"
Result_count = tempfolder +"\\Count.shp"
Resultintersection = tempfolder +"\\intersect.shp"
Results_Midpoint=tempfolder +"\\midpoint.shp"
Results_Midpoint2=tempfolder +"\\midpoint2.shp"

from qgis import processing
import pandas as pd 

# Reading the inputs and importing the layers
bufferdistance= bufferdistance_inft/363971.1025
layer1 = iface.addVectorLayer(fn1, ' ', 'ogr')
layer2 = iface.addVectorLayer(fn2, ' ', 'ogr')
fields1 = layer1.fields()
fields2 = layer2.fields()
feats1 = layer1.getFeatures()
feats2 = layer2.getFeatures()

# Adding a buffer to the segments
writer1 = QgsVectorFileWriter(Outfn, 'UTF-8', fields1, QgsWkbTypes.Polygon, layer1.sourceCrs(), 'ESRI shapefile')
for feat1 in feats1:
    geom1 = feat1.geometry()
    buff = geom1.buffer(bufferdistance, 5)
    feat1.setGeometry(buff)
    writer1.addFeature(feat1)
    
iface.addVectorLayer(Outfn, '', 'ogr')
del(writer1)

# counting the number of restaurants in the created buffer
processing.run("qgis:countpointsinpolygon", { 'CLASSFIELD' : '', 'FIELD' : 'RESTAURANT_COUNT', 'OUTPUT' : Result_count, 'POINTS' : fn2, 'POLYGONS' : Outfn, 'WEIGHT' : '' })
segmentid =[]
numberofrests=[]
layerofcount = iface.addVectorLayer(Result_count, ' ', 'ogr')
fieldsofcount = layerofcount.fields()
featsofcounut = layerofcount.getFeatures()

for feature in featsofcounut:
    segmentid.append(feature["SEGMENT"])
    numberofrests.append(feature["RESTAURANT"])
    
segmentid = pd.DataFrame(segmentid,columns=["SEGMENT"])
numberofrests = pd.DataFrame(numberofrests,columns=["RESTAURANT_COUNT"])
Results1=pd.concat([segmentid,numberofrests], axis=1)

# Saving the results of the first task
Results1.to_csv(Results1csv,index=False)
###############################################################################################
# Preparing some files for Task 2

# Excluding the points that are outside the buffer for task 2
processing.run("gdal:pointsalonglines", { 'DISTANCE' : 0.5, 'GEOMETRY' : 'geometry', 'INPUT' : fn1, 'OPTIONS' : '', 'OUTPUT' : Results_Midpoint })
layer_midpoints = iface.addVectorLayer(Results_Midpoint, ' ', 'ogr')
fields_midpoints = layer_midpoints.fields()
feats_midpoints = layer_midpoints.getFeatures()

# Adding the centroid of each segment
processing.run("qgis:exportaddgeometrycolumns", { 'CALC_METHOD' : 0, 'INPUT' : Results_Midpoint, 'OUTPUT' : Results_Midpoint2})
layer_midpoints2 = iface.addVectorLayer(Results_Midpoint2, ' ', 'ogr')
fields_midpoints2 = layer_midpoints2.fields()
feats_midpoints2 = layer_midpoints2.getFeatures()

# Finding the restaurant points of interest
processing.run("qgis:intersection", { 'INPUT' : fn2, 'INPUT_FIELDS' : [], 'OUTPUT' : Resultintersection, 'OVERLAY' : Result_count, 'OVERLAY_FIELDS' : [], 'OVERLAY_FIELDS_PREFIX' : '' })
layer_intersect = iface.addVectorLayer(Resultintersection, ' ', 'ogr')
fields_intersect = layer_intersect.fields()
feats_intersect = layer_intersect.getFeatures()

# Approximating the selected restauraunts to the nearest midpoint segment with coordinates
csvField = 'SEGMENT'
shpField = 'SEGMENT'
joinObject = QgsVectorLayerJoinInfo()
joinObject.setJoinFieldName(csvField)
joinObject.setTargetFieldName(shpField)
joinObject.setJoinLayerId(layer_midpoints2.id())
joinObject.setUsingMemoryCache(True)
joinObject.setJoinLayer(layer_midpoints2)
layer_intersect.addJoin(joinObject)

# To continue in Task 2 There are multiple issues to be considered:
# 1- QGIS can solve Problem2 through the script but it requires extra time compared to PostGIS solutions.
# 2- Some restaurant points found to be close to multiple segments. To avoid double counting, the duplicates are deleted in which only one point is associated with one segment
# 3- To continue in Task2, we need the attributes of "midpoints2" as CSV file
