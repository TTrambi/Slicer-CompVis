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
from vtk.util import numpy_support

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

     # Set Advanced Parameters Collapsible Button
    self.parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    self.parametersCollapsibleButton.text = "Set Advanced Segmentation Parameters"
    #self.TumorSegmentationLayout.addWidget(self.parametersCollapsibleButton)
    self.formLayout.addWidget(self.parametersCollapsibleButton)
    self.parametersCollapsibleButton.collapsed = True
    # Layout within the collapsible button
    self.parametersLayout = qt.QFormLayout(self.parametersCollapsibleButton)
    # Set Minimum Threshold of Percentage Increase to First Post-Contrast Image
    self.inputMinimumThreshold = qt.QLabel("Minimum Threshold of Increase", self.parametersCollapsibleButton)
    self.inputMinimumThreshold.setToolTip('Minimum Threshold of Percentage Increase (Pre- to First Post-contrast (Range: 10% to 150%)')
    self.inputSelectorMinimumThreshold = qt.QDoubleSpinBox(self.parametersCollapsibleButton)
    self.inputSelectorMinimumThreshold.setSuffix("%")
    self.inputSelectorMinimumThreshold.singleStep = (1)
    self.inputSelectorMinimumThreshold.minimum = (10)
    self.inputSelectorMinimumThreshold.maximum = (150)
    self.inputSelectorMinimumThreshold.value = (75)
    self.inputSelectorMinimumThreshold.setToolTip('Minimum Threshold of Percentage Increase (Pre- to First Post-contrast (Range: 10% to 150%)')
    self.parametersLayout.addRow(self.inputMinimumThreshold, self.inputSelectorMinimumThreshold)
    # Curve 1 Type Parameters (Slopes from First to Fourth Post-Contrast Images)
    self.inputCurve1 = qt.QLabel("Type 1 (Persistent) Curve Minimum Slope", self.parametersCollapsibleButton)
    self.inputCurve1.setToolTip('Minimum Slope of Delayed Curve to classify as Persistent (Range: 0.02 to 0.3)')
    self.inputSelectorCurve1 = qt.QDoubleSpinBox(self.parametersCollapsibleButton)
    self.inputSelectorCurve1.singleStep = (0.02)
    self.inputSelectorCurve1.minimum = (0.02)
    self.inputSelectorCurve1.maximum = (0.3)
    self.inputSelectorCurve1.value = (0.20)
    self.inputSelectorCurve1.setToolTip('Minimum Slope of Delayed Curve to classify as Persistent (Range: 0.02 to 0.3)')
    self.parametersLayout.addRow(self.inputCurve1, self.inputSelectorCurve1)
    # Curve 3 Type Parameters (Slopes from First to Fourth Post-Contrast Images)
    self.inputCurve3 = qt.QLabel("Type 3 (Washout) Curve Maximum Slope", self.parametersCollapsibleButton)
    self.inputCurve3.setToolTip('Maximum Slope of Delayed Curve to classify as Washout (Range: -0.02 to -0.3)')
    self.inputSelectorCurve3 = qt.QDoubleSpinBox(self.parametersCollapsibleButton)
    self.inputSelectorCurve3.singleStep = (0.02)
    self.inputSelectorCurve3.setPrefix("-")
    self.inputSelectorCurve3.minimum = (0.02)
    self.inputSelectorCurve3.maximum = (0.30)
    self.inputSelectorCurve3.value = (0.20)
    self.inputSelectorCurve3.setToolTip('Maximum Slope of Delayed Curve to classify as Washout (Range: -0.02 to -0.3)')
    self.parametersLayout.addRow(self.inputCurve3, self.inputSelectorCurve3)


    # Path input for dicom data to analyze
    self.inputPath = qt.QFileDialog()
    self.inputPath.setFileMode(qt.QFileDialog.Directory)


    #self.formLayout.addWidget(self.parametersCollapsibleButton)
    self.formLayout.addWidget(self.inputPath)

    # add vertical spacer
    self.layout.addStretch(1)

    # connect directory widget with function
    self.inputPath.connect('accepted()', self.createLogic)


  def createLogic(self):
    pathToDICOM = self.inputPath.directory().absolutePath()
    minThreshold = (self.inputSelectorMinimumThreshold.value)/(100)
    curve3Maximum = -1 * (self.inputSelectorCurve3.value)
    curve1Minimum = self.inputSelectorCurve1.value
    self.logic = AutoSegmentationLogic(pathToDICOM, minThreshold, curve1Minimum, curve3Maximum)

#
# AutoSegmentationLogic
#
class AutoSegmentationLogic(ScriptedLoadableModuleLogic):

  def __init__(self, pathToDICOM, minTreshold, curve1Minimum, curve3Maximum):
    self.pathToDICOM = pathToDICOM
    self.minTreshold = minTreshold
    self.curve1Minimum = curve1Minimum
    self.curve3Maximum = curve3Maximum
    logging.info("logic created")
    logging.info("parameters:")
    logging.info(pathToDICOM)
    logging.info(minTreshold)
    logging.info(curve1Minimum)
    logging.info(curve3Maximum)
    
    self.dicomDataNumpyArrays = self.readData()
    self.initialRiseArray = self.calcInitialRise()
    self.slopeArray = self.calcSlope()
    logging.info("initial rise and slope calculated")

    #boolean array with targeted voxels
    self.targetVoxels = self.getTargetedVoxels()
    self.persistenceVoxels = self.getPersistanceVoxels()
    self.plateauVoxels = self.getPlateauVoxels()
    self.washoutVoxels = self.getWashoutVoxels()


    #convert numpy to vtkImageData
    VTKTargetVoxelsImageImport =  vtk.vtkImageImport()

    w, d, h = self.plateauVoxels.shape

    self.plateauVoxels[w-1,:,:] = 0
    self.plateauVoxels[:,0,:] = 0
    self.plateauVoxels[:,d-1,:] = 0
    self.plateauVoxels[:,:,0] = 0
    self.plateauVoxels[:,:,h-1] = 0
    array_string = self.plateauVoxels.tostring()
    

    VTKTargetVoxelsImageImport.CopyImportVoidPointer(array_string, len(array_string))
    VTKTargetVoxelsImageImport.SetDataScalarTypeToUnsignedChar()
    VTKTargetVoxelsImageImport.SetNumberOfScalarComponents(1)

    VTKTargetVoxelsImageImport.SetDataExtent(0,h-1,0,d-1,0,w-1)
    VTKTargetVoxelsImageImport.SetWholeExtent(0,h-1,0,d-1,0,w-1)
    VTKTargetVoxelsImageImport.SetDataSpacing(1,1,1)



    logging.info("imageImporter set up")

    threshold = vtk.vtkImageThreshold()
    threshold.SetInputConnection(VTKTargetVoxelsImageImport.GetOutputPort())
    threshold.ThresholdByLower(0)
    threshold.ReplaceInOn()
    threshold.SetInValue(0)
    threshold.SetOutValue(1)
    threshold.Update()
    
    dmc = vtk.vtkDiscreteMarchingCubes()
    dmc.SetInputConnection(threshold.GetOutputPort())
    dmc.GenerateValues(1,1,1)
    dmc.Update()

    logging.info("marching curbes applied")

    writer = vtk.vtkSTLWriter()
    writer.SetInputConnection(dmc.GetOutputPort())
    writer.SetFileTypeToBinary()
    writer.SetFileName("test.stl")
    writer.Write()

    logging.info("finished writing to file")

    self.modelNode = slicer.vtkMRMLModelNode()
    #self.modelNode.SetAndObservePolyData(dmc.GetOutput())
    self.modelNode.SetPolyDataConnection(dmc.GetOutputPort())
    slicer.mrmlScene.AddNode(self.modelNode)

    #self.volNode.UpdateScene()


  def readData(self):
    filesDCM = []
    for dirName, subdirList, fileList in os.walk(self.pathToDICOM):
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
    dicomNumpyArrays = []
    for dicomSeries in dicomDataContrastVolumes:
      dicomNumpyArrays.append(self.createNumpyArray(dicomSeries))

    logging.info("3D Numpy Arrays created")

    return dicomNumpyArrays

  # Computes percentage increase from baseline (pre-contrast) at each voxel for each volume as numpy arrays.
  def calcInitialRise(self):
    # Initial Rise at each voxel (percentage increase from pre-contrast to first post-contrast)
    return ((self.dicomDataNumpyArrays[1]).__truediv__(self.dicomDataNumpyArrays[0]+1.0))-1.0

  def calcSlope(self):
    # Compute slope at each voxel from first to fourth volume to determine curve type
    return (self.dicomDataNumpyArrays[-1] - self.dicomDataNumpyArrays[1]).__truediv__(self.dicomDataNumpyArrays[1]+1.0)

  def getTargetedVoxels(self):
    targetVoxels = (self.initialRiseArray > self.minTreshold) & (self.dicomDataNumpyArrays[0] > self.minTreshold)
    return targetVoxels

  def getPersistanceVoxels(self):
    persistenceVoxels = numpy.zeros((256,256,60))
    for x in range(0,255):
      for y in range(0,255):
        for z in range(0,59):
          if (self.slopeArray[x,y,z] > self.curve3Maximum) & (self.slopeArray[x,y,z] < self.curve1Minimum) & (self.targetVoxels[x,y,z] > 100):
            persistenceVoxels[x,y,z] = 100
    return persistenceVoxels

    #persistenceVoxels = numpy.where((self.slopeArray > self.curve1Minimum) & (self.targetVoxels))
    #return persistenceVoxels

  def getPlateauVoxels(self):
    plateauVoxels = (self.slopeArray > self.curve3Maximum) & (self.slopeArray < self.curve1Minimum) & (self.targetVoxels)
    return plateauVoxels

  def getWashoutVoxels(self):
    washoutVoxels = numpy.where((self.slopeArray < self.curve3Maximum) & (self.targetVoxels))
    return washoutVoxels


  ### helper and converter functions ###
  def createNumpyArray(self, dicomSeries):
    #convert sets into numpy arrays to modify voxels in a new vtkMRMLScalarVolumeNode
    constPixelDims = (int(dicomSeries[0].Rows), int(dicomSeries[0].Columns), len(dicomSeries))
    constPixelSpacing = (float(dicomSeries[0].PixelSpacing[0]), float(dicomSeries[0].PixelSpacing[1]),float(dicomSeries[0].SliceThickness))
    numpyArray = numpy.zeros(constPixelDims, dtype=dicomSeries[0].pixel_array.dtype)
    for dicomData in dicomSeries:
      numpyArray[:,:, dicomSeries.index(dicomData)] = dicomData.pixel_array
    return numpyArray


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
