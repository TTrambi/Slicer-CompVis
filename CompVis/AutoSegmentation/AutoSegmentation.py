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

    # Path input for dicom data to analyze
    self.inputPath = qt.QFileDialog()
    self.inputPath.setFileMode(qt.QFileDialog.Directory)

    #self.inputPathCtk = ctk.ctkDICOMAppWidget()
    
    self.formLayout.addWidget(self.inputPath)
    #self.formLayout.addWidget(self.inputPathCtk)

    # add vertical spacer
    self.layout.addStretch(1)

    # connect directory widget with function
    self.inputPath.connect('accepted()', self.createLogic)
    #self.inputPathCtk.connect('onFileIndexed(const QString &filePath)', self.onModelSelectedInput)

  def createLogic(self):
    pathToDICOM = self.inputPath.directory().absolutePath()
    self.logic = AutoSegmentationLogic(pathToDICOM, 0.75, 0.2, -0.2)

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
    
    #self.persistenceVoxels = self.getPersistanceVoxels()
    #self.plateauVoxels = self.getPlateauVoxels()
    #self.washoutVoxels = self.getWashoutVoxels()

    numpy.savetxt('File.out', self.targetVoxels[:,:,30], delimiter=' ')

    #convert numpy to vtkImageData
    VTKTargetVoxelsImageImport =  vtk.vtkImageImport()

    array_string = self.targetVoxels.tostring()

    VTKTargetVoxelsImageImport.CopyImportVoidPointer(array_string, len(array_string))
    VTKTargetVoxelsImageImport.SetDataScalarTypeToUnsignedChar()
    VTKTargetVoxelsImageImport.SetNumberOfScalarComponents(1)

    w, d, h = self.targetVoxels.shape
    VTKTargetVoxelsImageImport.SetDataExtent(0,w-1,0,d-1,0,h-1)
    VTKTargetVoxelsImageImport.SetWholeExtent(0,w-1,0,d-1,0,h-1)
    VTKTargetVoxelsImageImport.SetDataSpacing(0.1,0.1,0.2)



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
    # x, y, z = self.dicomDataNumpyArrays[0].shape
    # targetVoxels = numpy.zeros((x,y,z))
    # for x in range(0,x-1):
    #   for y in range(0,y-1):
    #     for z in range(0,z-1):
    #       if (self.initialRiseArray[x,y,z] > self.minTreshold):
    #         targetVoxels[x,y,z] = self.dicomDataNumpyArrays[0][x,y,z]
    #       else:
    #         targetVoxels[x,y,z] = 0
    # return targetVoxels

    targetVoxels = (self.initialRiseArray > self.minTreshold) & (self.dicomDataNumpyArrays[0] > 10)
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
    plateuaVoxels = numpy.where( (self.slopeArray > self.curve3Maximum) & (self.slopeArray < self.curve1Minimum) & (self.targetVoxels) )
    return plateauVoxels

  def getWashoutVoxels(self):
    washoutVoxels = numpy.where((self.slopeArray < self.curve3Maximum) & (self.targetVoxels))
    return washoutVoxels



  # def arrayProcessing(self):
  #   # Create Boolean array, target_voxels, with target voxel indices highlighted as True 
  #   # Assigns color to SegmentCAD Label map index if corresponding slope condition is satisfied where target_voxel is True 
      
  #   target_voxels = (self.nodeArrayInitialRise > self.minTreshold) & (self.dicomNumpyArrays[0] > 100)
  
  #   # yellow (Plateau Slope)
  #   self.nodeArraySegmentCADLabel[numpy.where( (self.slopeArray1_4 > -0.2) & (self.slopeArray1_4 < 0.2) & (target_voxels) )] = 291
    
  #   # blue (slope of curve1 min = 0.2(default), Persistent Slope)
  #   self.nodeArraySegmentCADLabel[numpy.where((self.slopeArray1_4 > 0.2) & (target_voxels))] = 306
    
  #   # red (slope of curve3 max = -0.2(default), Washout Slope )
  #   self.nodeArraySegmentCADLabel[numpy.where((self.slopeArray1_4 < -0.2) & (target_voxels))] = 32



  ### helper and converter functions ###
  def createNumpyArray(self, dicomSeries):
    #convert sets into numpy arrays to modify voxels in a new vtkMRMLScalarVolumeNode
    constPixelDims = (int(dicomSeries[0].Rows), int(dicomSeries[0].Columns), len(dicomSeries))
    constPixelSpacing = (float(dicomSeries[0].PixelSpacing[0]), float(dicomSeries[0].PixelSpacing[1]),float(dicomSeries[0].SliceThickness))
    numpyArray = numpy.zeros(constPixelDims, dtype=dicomSeries[0].pixel_array.dtype)
    for dicomData in dicomSeries:
      numpyArray[:,:, dicomSeries.index(dicomData)] = dicomData.pixel_array
    return numpyArray

  def numpyArraytoNumpyBooleanArray(self, numpyArray):
    numpyBooleanArray = numpyArray > 0
    numpyBooleanArray.astype(numpy.Boolean)

  def numpyBooleanArrayToMesh(self, numpyBooleanArray):
    VTK_data = numpy_support.numpy_to_vtk(numpyBooleanArray.ravel(), deep=True, array_type=vtk.VTK_BOOLEAN)


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
