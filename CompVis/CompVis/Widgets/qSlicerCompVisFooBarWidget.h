/*==============================================================================

  Program: 3D Slicer

  Copyright (c) Kitware Inc.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
  and was partially funded by NIH grant 3P41RR013218-12S1

==============================================================================*/

#ifndef __qSlicerCompVisFooBarWidget_h
#define __qSlicerCompVisFooBarWidget_h

// Qt includes
#include <QWidget>

// FooBar Widgets includes
#include "qSlicerCompVisModuleWidgetsExport.h"

class qSlicerCompVisFooBarWidgetPrivate;

/// \ingroup Slicer_QtModules_CompVis
class Q_SLICER_MODULE_COMPVIS_WIDGETS_EXPORT qSlicerCompVisFooBarWidget
  : public QWidget
{
  Q_OBJECT
public:
  typedef QWidget Superclass;
  qSlicerCompVisFooBarWidget(QWidget *parent=0);
  virtual ~qSlicerCompVisFooBarWidget();

protected slots:

protected:
  QScopedPointer<qSlicerCompVisFooBarWidgetPrivate> d_ptr;

private:
  Q_DECLARE_PRIVATE(qSlicerCompVisFooBarWidget);
  Q_DISABLE_COPY(qSlicerCompVisFooBarWidget);
};

#endif
