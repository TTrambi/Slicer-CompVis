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

    #convert sets into numpy arrays to modify voxels in a new vtkMRMLScalarVolumeNode
    constPixelDims = (int(dicomData[0].Rows), int(dicomData[0].Columns), len(dicomDataContrastVolumes[0]))
    constPixelSpacing = (float(dicomData[0].PixelSpacing[0]), float(dicomData[0].PixelSpacing[1]),float(dicomData[0].SliceThickness))


  def onModelSelectedInput(self):
  	logging.info('Model selected')

  def separateData(self, filesDCM):
  	logging.info('Separating Data')
  	#first sort by acquisition number then sort by 


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
