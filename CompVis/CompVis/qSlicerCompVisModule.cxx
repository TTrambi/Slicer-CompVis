/*==============================================================================

  Program: 3D Slicer

  Portions (c) Copyright Brigham and Women's Hospital (BWH) All Rights Reserved.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

==============================================================================*/

// Qt includes
#include <QtPlugin>

// CompVis Logic includes
#include <vtkSlicerCompVisLogic.h>

// CompVis includes
#include "qSlicerCompVisModule.h"
#include "qSlicerCompVisModuleWidget.h"

//-----------------------------------------------------------------------------
Q_EXPORT_PLUGIN2(qSlicerCompVisModule, qSlicerCompVisModule);

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ExtensionTemplate
class qSlicerCompVisModulePrivate
{
public:
  qSlicerCompVisModulePrivate();
};

//-----------------------------------------------------------------------------
// qSlicerCompVisModulePrivate methods

//-----------------------------------------------------------------------------
qSlicerCompVisModulePrivate::qSlicerCompVisModulePrivate()
{
}

//-----------------------------------------------------------------------------
// qSlicerCompVisModule methods

//-----------------------------------------------------------------------------
qSlicerCompVisModule::qSlicerCompVisModule(QObject* _parent)
  : Superclass(_parent)
  , d_ptr(new qSlicerCompVisModulePrivate)
{
}

//-----------------------------------------------------------------------------
qSlicerCompVisModule::~qSlicerCompVisModule()
{
}

//-----------------------------------------------------------------------------
QString qSlicerCompVisModule::helpText() const
{
  return "This is a loadable module that can be bundled in an extension";
}

//-----------------------------------------------------------------------------
QString qSlicerCompVisModule::acknowledgementText() const
{
  return "This work was partially funded by NIH grant NXNNXXNNNNNN-NNXN";
}

//-----------------------------------------------------------------------------
QStringList qSlicerCompVisModule::contributors() const
{
  QStringList moduleContributors;
  moduleContributors << QString("John Doe (AnyWare Corp.)");
  return moduleContributors;
}

//-----------------------------------------------------------------------------
QIcon qSlicerCompVisModule::icon() const
{
  return QIcon(":/Icons/CompVis.png");
}

//-----------------------------------------------------------------------------
QStringList qSlicerCompVisModule::categories() const
{
  return QStringList() << "Examples";
}

//-----------------------------------------------------------------------------
QStringList qSlicerCompVisModule::dependencies() const
{
  return QStringList();
}

//-----------------------------------------------------------------------------
void qSlicerCompVisModule::setup()
{
  this->Superclass::setup();
}

//-----------------------------------------------------------------------------
qSlicerAbstractModuleRepresentation* qSlicerCompVisModule
::createWidgetRepresentation()
{
  return new qSlicerCompVisModuleWidget;
}

//-----------------------------------------------------------------------------
vtkMRMLAbstractLogic* qSlicerCompVisModule::createLogic()
{
  return vtkSlicerCompVisLogic::New();
}
