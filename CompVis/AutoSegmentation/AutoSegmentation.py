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
