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
import qt
import __main__





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

    # mainWidget = qt.QWidget()
    # vlayout = qt.QVBoxLayout()
    # mainWidget.setLayout(vlayout)

    # layoutManager = slicer.qMRMLLayoutWidget()
    # layoutManager.setMRMLScene(slicer.mrmlScene)
    # layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
    # vlayout.addWidget(layoutManager)

    # hlayout = qt.QHBoxLayout()
    # vlayout.addLayout(hlayout)

    # loadDataButton = qt.QPushButton("Load Data")
    # hlayout.addWidget(loadDataButton)
    # loadDataButton.connect('clicked()', slicer.util.openAddVolumeDialog)

    # saveDataButton = qt.QPushButton("Save Data")
    # hlayout.addWidget(saveDataButton)
    # saveDataButton.connect('clicked()', slicer.util.openSaveDataDialog)

    # moduleSelector = slicer.qSlicerModuleSelectorToolBar()sc
    # moduleSelector.setModuleManager(slicer.app.moduleManager())
    # hlayout.addWidget(moduleSelector)
    # moduleSelector.connect('moduleSelected(QString)', onModuleSelected)

    # tabWidget = qt.QTabWidget()
    # vlayout.addWidget(tabWidget)

    # mainWidget.show()

    # __main__.mainWidget = mainWidget

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
    self.inputSelectorCurve1.maximum = (0.30)
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

  def __init__(self, pathToDICOM, minThreshold, curve1Minimum, curve3Maximum):
    self.pathToDICOM = pathToDICOM
    self.minThreshold = minThreshold
    self.curve1Minimum = curve1Minimum
    self.curve3Maximum = curve3Maximum

    self.dicomDataNumpyArrays = self.readData()
    self.initialRiseArray = self.calcInitialRise()
    self.slopeArray = self.calcSlope()

    self.roi = self.createROI()

    #boolean array with targeted voxels
    self.targetVoxels = self.getTargetedVoxels() 
    self.persistenceVoxels = self.getPersistanceVoxels()
    self.plateauVoxels = self.getPlateauVoxels()
    self.washoutVoxels = self.getWashoutVoxels()

    #self.createAndSaveVolume(self.persistenceVoxels, "persistence.stl")
    #self.createAndSaveVolume(self.plateauVoxels, "plateau.stl")
    self.createAndSaveVolume(self.washoutVoxels, "washout.stl")



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


    #convert sets into numpy Arrays
    dicomNumpyArrays = []
    for dicomSeries in dicomDataContrastVolumes:
      dicomNumpyArrays.append(self.createNumpyArray(dicomSeries))


    return dicomNumpyArrays

  # Computes percentage increase from baseline (pre-contrast) at each voxel for each volume as numpy arrays.
  def calcInitialRise(self):
    # Initial Rise at each voxel (percentage increase from pre-contrast to first post-contrast)

    temp = numpy.divide((self.dicomDataNumpyArrays[1] - self.dicomDataNumpyArrays[0]), self.dicomDataNumpyArrays[0])
    temp = numpy.nan_to_num(temp)
    return temp
    #return ((self.dicomDataNumpyArrays[1]).__truediv__(self.dicomDataNumpyArrays[0]+1.0))-1.0

  def calcSlope(self):
    # Compute slope at each voxel from first to fourth volume to determine curve type
    temp = numpy.divide((self.dicomDataNumpyArrays[-1] - self.dicomDataNumpyArrays[1]), self.dicomDataNumpyArrays[1])
    temp = numpy.nan_to_num(temp)
    return temp
    #return (self.dicomDataNumpyArrays[-1] - self.dicomDataNumpyArrays[1]).__truediv__(self.dicomDataNumpyArrays[1]+1.0)

  def getTargetedVoxels(self):
    targetVoxels = (self.initialRiseArray > self.minThreshold) & (self.dicomDataNumpyArrays[0] > 20)
    targetVoxels = targetVoxels & self.roi
    return targetVoxels

  def getPersistanceVoxels(self):
    persistenceVoxels = (self.slopeArray > self.curve1Minimum) & (self.targetVoxels)
    return persistenceVoxels

  def getPlateauVoxels(self):
    plateauVoxels = (self.slopeArray > self.curve3Maximum) & (self.slopeArray < self.curve1Minimum) & (self.targetVoxels)
    return plateauVoxels

  def getWashoutVoxels(self):
    washoutVoxels = (self.slopeArray < self.curve3Maximum) & (self.targetVoxels)
    return washoutVoxels


  def createAndSaveVolume(self, numpyBoolArray, name):
    #convert numpy to vtkImageData
    VTKTargetVoxelsImageImport =  vtk.vtkImageImport()

    numpyBoolArray = numpy.flipud(numpyBoolArray)
    numpyBoolArray = numpy.fliplr(numpyBoolArray)
    w, d, h = numpyBoolArray.shape

    numpyBoolArray[w-1,:,:] = 0
    numpyBoolArray[:,0,:] = 0
    numpyBoolArray[:,d-1,:] = 0
    numpyBoolArray[:,:,0] = 0
    numpyBoolArray[:,:,h-1] = 0
    array_string = numpyBoolArray.tostring()
    

    VTKTargetVoxelsImageImport.CopyImportVoidPointer(array_string, len(array_string))
    VTKTargetVoxelsImageImport.SetDataScalarTypeToUnsignedChar()
    VTKTargetVoxelsImageImport.SetNumberOfScalarComponents(1)

    VTKTargetVoxelsImageImport.SetDataExtent(0,h-1,0,d-1,0,w-1)
    VTKTargetVoxelsImageImport.SetWholeExtent(0,h-1,0,d-1,0,w-1)
    VTKTargetVoxelsImageImport.SetDataSpacing(1,1,1)


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

    smoothVolume = vtk.vtkSmoothPolyDataFilter()
    smoothVolume.SetInputConnection(dmc.GetOutputPort())
    smoothVolume.SetNumberOfIterations(1)
    smoothVolume.SetRelaxationFactor(0.5)
    smoothVolume.FeatureEdgeSmoothingOff()
    smoothVolume.BoundarySmoothingOn()
    smoothVolume.Update()


    slicer.modules.models.logic().AddModel(smoothVolume.GetOutputPort())

    #slicer.modules.models.logic().AddModel(dmc.GetOutput())

    biggestArea = vtk.vtkPolyDataConnectivityFilter()
    biggestArea.SetInputConnection(smoothVolume.GetOutputPort())
    biggestArea.SetExtractionModeToLargestRegion()
    biggestArea.Update()

    #slicer.modules.models.logic().AddModel(biggestArea.GetOutputPort())

    #modelNode = slicer.vtkMRMLScalarVolumeNode()
    #modelNode.SetPolyDataConnection(smoothVolume.GetOutputPort())
    #slicer.mrmlScene.AddNode(modelNode)
    #slicer.mrmlScene.SetAndObserveMRMLScene()

    writer = vtk.vtkSTLWriter()
    writer.SetInputConnection(smoothVolume.GetOutputPort())
    writer.SetFileTypeToBinary()
    writer.SetFileName(name)
    writer.Write()

    logging.info("finished writing to file")

  ### helper and converter functions ###
  def createNumpyArray(self, dicomSeries):
    #convert sets into numpy arrays to modify voxels in a new vtkMRMLScalarVolumeNode
    constPixelDims = (int(dicomSeries[0].Rows), int(dicomSeries[0].Columns), len(dicomSeries))
    constPixelSpacing = (float(dicomSeries[0].PixelSpacing[0]), float(dicomSeries[0].PixelSpacing[1]),float(dicomSeries[0].SliceThickness))
    numpyArray = numpy.zeros(constPixelDims, dtype=dicomSeries[0].pixel_array.dtype)
    for dicomData in dicomSeries:
      numpyArray[:,:, dicomSeries.index(dicomData)] = dicomData.pixel_array
    return numpyArray

  def createROI(self):
    roi = numpy.zeros(self.dicomDataNumpyArrays[0].shape)
    thresholdedArray = (self.dicomDataNumpyArrays[0] > 20)

    firstValue = 0
    y, x, z = roi.shape


    for i in xrange(0, x-1):
      if thresholdedArray[255, i, 29] == True:
        firstValue = i
        break

    roi[:,0:firstValue,:] = True

    return roi.astype('bool_')

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

#
# AutoSegmentationSliceletWidget
#
class AutoSegmentationSliceletWidget:
  def __init__(self, parent=None):
    try:
      parent
      self.parent = parent

    except Exception, e:
      import traceback
      traceback.print_exc()
      logging.error("There is no parent to GelDosimetryAnalysisSliceletWidget!")

#
# SliceletMainFrame
#   Handles the event when the slicelet is hidden (its window closed)
#
class SliceletMainFrame(qt.QDialog):
  def setSlicelet(self, slicelet):
    self.slicelet = slicelet

  def hideEvent(self, event):
    self.slicelet.disconnect()

    import gc
    refs = gc.get_referrers(self.slicelet)
    if len(refs) > 1:
      # logging.debug('Stuck slicelet references (' + repr(len(refs)) + '):\n' + repr(refs))
      pass

    slicer.gelDosimetrySliceletInstance = None
    self.slicelet = None
    self.deleteLater()

#
# GelDosimetryAnalysisSlicelet
#
class AutoSegmentationSlicelet(VTKObservationMixin):
  def __init__(self, parent, developerMode=False, widgetClass=None):
    VTKObservationMixin.__init__(self)
    # Set up main frame
    self.parent = parent
    self.parent.setLayout(qt.QHBoxLayout())

    self.layout = self.parent.layout()
    self.layout.setMargin(0)
    self.layout.setSpacing(0)

    self.sliceletPanel = qt.QFrame(self.parent)
    self.sliceletPanelLayout = qt.QVBoxLayout(self.sliceletPanel)
    self.sliceletPanelLayout.setMargin(4)
    self.sliceletPanelLayout.setSpacing(0)
    self.layout.addWidget(self.sliceletPanel,1)

def disconnect(self):
    "asdf"