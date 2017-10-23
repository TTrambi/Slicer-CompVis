import os
import unittest
import vtk
import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import *
import logging
import dicom
import numpy

#
# AutoSegmentation
#
class AutoSegmentation(ScriptedLoadableModule):
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    # TODO make this more human readable by adding spaces
    self.parent.title = "AutoSegmentation"
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Thomas Tramberger (TU Wien)"]
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension. It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""  # replace with organization, grant and thanks.

#
# AutoSegmentationWidget
#
class AutoSegmentationWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  def setup(self):
    # gui for testing and reloading, /todo remove at end
    ScriptedLoadableModuleWidget.setup(self)

    # Collapsible button
    self.collapsibleButton = ctk.ctkCollapsibleButton()
    self.collapsibleButton.text = "AutoSegmentation"
    self.layout.addWidget(self.collapsibleButton)

    # Layout for path input and process button
    self.formLayout = qt.QFormLayout(self.collapsibleButton)

    # Path input for dicom data to analyze
    self.inputPath = qt.QFileDialog()
    self.inputPath.setFileMode(qt.QFileDialog.Directory)

    #self.inputPathCtk = ctk.ctkDICOMAppWidget()
    
    self.formLayout.addWidget(self.inputPath)
    #self.formLayout.addWidget(self.inputPathCtk)

    # add vertical spacer
    self.layout.addStretch(1)

    # connect directory widget with function
    self.inputPath.connect('accepted()', self.readInData)
    #self.inputPathCtk.connect('onFileIndexed(const QString &filePath)', self.onModelSelectedInput)

  def readInData(self):
    pathToDICOM = self.inputPath.directory().absolutePath()
    logging.info('Path set to:' + pathToDICOM)
    
    # reader = vtk.vtkDICOMImageReader()
    # reader.SetDirectoryName(pathToDICOM)
    # reader.Update()
    
    # print reader

    # Load dimensions using `GetDataExtent`
    #_extent = reader.GetDataExtent()
    #ConstPixelDims = [_extent[1]-_extent[0]+1, _extent[3]-_extent[2]+1, _extent[5]-_extent[4]+1]

    # Load spacing values
    #ConstPixelSpacing = reader.GetPixelSpacing()




    filesDCM = []
    for dirName, subdirList, fileList in os.walk(pathToDICOM):
      for filename in fileList:
        if ".dcm" in filename.lower():
          filesDCM.append(os.path.join(dirName, filename))


    #load all dicom data 
    dicomData = []
    for files in filesDCM:
      dicomData.append(dicom.read_file(files)) 

   	#sort dicom data by instance number
    dicomData.sort(key=lambda dicomData: dicomData.InstanceNumber)

    #separate data to their contrast volumes
    dicomDataContrastVolumes = []
    firstContrastVolume = []
    dicomDataContrastVolumes.append(firstContrastVolume)
    contrastVolumeIndexHelper = 0
    for i in range(0,len(dicomData)-1):
      if dicomData[i].SliceLocation < dicomData[i+1].SliceLocation:
        dicomDataContrastVolumes[contrastVolumeIndexHelper].append(dicomData[i])
      else:
        dicomDataContrastVolumes[contrastVolumeIndexHelper].append(dicomData[i])
        contrastVolumeIndexHelper = contrastVolumeIndexHelper+1
        nextContrastVolume = []
        dicomDataContrastVolumes.append(nextContrastVolume)
    #assign last element
    dicomDataContrastVolumes[contrastVolumeIndexHelper].append(dicomData[-1])

    logging.info("Dicom data seperated into %i sets.", len(dicomDataContrastVolumes))


    #convert sets into numpy Arrays
    self.dicomNumpyArrays = []
    for dicomSeries in dicomDataContrastVolumes:
      self.dicomNumpyArrays.append(self.createNumpyArray(dicomSeries))

    logging.info("Numpy Arrays created")

    self.initializeNodeArrays()

    logging.info("SegmentationLabel initialized")

    print self.nodeArraySegmentCADLabel



  def createNumpyArray(self, dicomSeries):
    #convert sets into numpy arrays to modify voxels in a new vtkMRMLScalarVolumeNode
    constPixelDims = (int(dicomSeries[0].Rows), int(dicomSeries[0].Columns), len(dicomSeries))
    constPixelSpacing = (float(dicomSeries[0].PixelSpacing[0]), float(dicomSeries[0].PixelSpacing[1]),float(dicomSeries[0].SliceThickness))
    numpyArray = numpy.zeros(constPixelDims, dtype=dicomSeries[0].pixel_array.dtype)
    for dicomData in dicomSeries:
      numpyArray[:,:, dicomSeries.index(dicomData)] = dicomData.pixel_array
    return numpyArray

  def initializeNodeArrays (self):
    # Computes percentage increase from baseline (pre-contrast) at each voxel for each volume as numpy arrays.
    # Initializes a numpy array of zeroes as numpy.int16 vtkShortArray for the SegmentCAD label map output.
      
    # Initial Rise at each voxel (percentage increase from pre-contrast to first post-contrast)
    self.nodeArrayInitialRise = ((self.dicomNumpyArrays[1]).__truediv__(self.dicomNumpyArrays[0]+1.0))-1.0
    # Compute slope at each voxel from first to fourth volume to determine curve type
    self.slopeArray1_4 = (self.dicomNumpyArrays[-1] - self.dicomNumpyArrays[1]).__truediv__(self.dicomNumpyArrays[1]+1.0)
    # Initialize SegmentCAD label map as numpy array
    shape = self.dicomNumpyArrays[0].shape
    self.nodeArraySegmentCADLabel = numpy.zeros(shape, dtype=numpy.int16)


  def arrayProcessing(self):
    # Create Boolean array, target_voxels, with target voxel indices highlighted as True 
    # Assigns color to SegmentCAD Label map index if corresponding slope condition is satisfied where target_voxel is True 
      
    target_voxels = (self.nodeArrayInitialRise > 0.75) & (self.dicomNumpyArrays[0] > 100)
  
    # yellow (Plateau Slope)
    self.nodeArraySegmentCADLabel[numpy.where( (self.slopeArray1_4 > -0.2) & (self.slopeArray1_4 < 0.2) & (target_voxels) )] = 291
    
    # blue (slope of curve1 min = 0.2(default), Persistent Slope)
    self.nodeArraySegmentCADLabel[numpy.where((self.slopeArray1_4 > 0.2) & (target_voxels))] = 306
    
    # red (slope of curve3 max = -0.2(default), Washout Slope )
    self.nodeArraySegmentCADLabel[numpy.where((self.slopeArray1_4 < -0.2) & (target_voxels))] = 32

#
# AutoSegmentationLogic
#
class AutoSegmentationLogic(ScriptedLoadableModuleLogic):

  def something():
	print "asdf"


#
# AutoSegmentationLogic
#
class AutoSegmentationTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  # def setUp(self):
   # slicer.mrmlScene.Clear(0)
