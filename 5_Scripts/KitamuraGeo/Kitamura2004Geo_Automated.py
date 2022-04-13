# Python Script, API Version = V19
# Script for creating bone + implant + periimplantitis region geometry,
# then performs boolean operations to obtain final FEA geometry.
# Author: Bruno Luna
# Date (start): 24.08.21

#---------------General-------------------
# Imported modules
import os

# Delete all objects to initalize script
ClearAll()

# Read all input parameters (if not defined, ask user with suggested default values)
# Note that "script parameters" always have priority over "user input" parameters)
# Outer Box (plus call to user input, in case parameters not available)
try:
    Parameters.xb1_Par and Parameters.yb1_Par and Parameters.zb1_Par
except:
    xb1MM = 16
    yb1MM = 26
    zb1MM = 18*2
    tb1MM = 1.3
    hImpMM = 10
    rImpMM = 2.0 
    pDamVMM = 1.3
    pDamHMM = 1.0
    result = Beta.InputHelper.PauseAndGetInput("My interactive tool", xb1MM, yb1MM, zb1MM, tb1MM, hImpMM, rImpMM, pDamVMM, pDamHMM)
    xb1 = [MM(xb1MM), MM(yb1MM), MM(zb1MM)]
else:
    xb1 = [MM(Parameters.xb1_Par), MM(Parameters.yb1_Par), MM(Parameters.zb1_Par)]
    hImpMM = 10 
    rImpMM = 2.0 
    
# Cortical bone thickness
try:
    Parameters.t_Par
except:
    tb1 = MM(tb1MM)
else:
    tb1 = MM(Parameters.t_Par)
    
# Implant height (inside bone)
try:
    Parameters.impHeight_Par
except:
    hImp = MM(hImpMM)
else:
    hImp = MM(Parameters.impHeight_Par)
    
# Implant radius (not diameter!)    
try:
    Parameters.impRadius_Par
except:
    rImp = MM(rImpMM)
else:
    rImp = MM(Parameters.impRadius_Par)
    
# Periimplant vertical damage
try:
    Parameters.periDamageVer_Par
except:
    pDamV = MM(pDamVMM)
else:
    pDamV = MM(Parameters.periDamageVer_Par)

# Periimplant horizontal damage
try:
    Parameters.periDamageHor_Par
except:
    pDamH = MM(pDamHMM)
else:
    pDamH = MM(Parameters.periDamageHor_Par)

# Define bone vertical periimplantitis damage
# i.e., in case no horiz. damage present, assume uniform vert. damage
if pDamH == 0.0:
    xb1[1] = xb1[1] - pDamV
    hImp = hImp - pDamV
    uniformDamage = True
else:
    uniformDamage = False
                
# Set Sketch Plane
sectionPlane = Plane.PlaneZX
result = ViewHelper.SetSketchPlane(sectionPlane, None)
# EndBlock

# Set general origin (0(Zero)=Origin)
x0 = [MM(0),  MM(0),  MM(0)]
originPoint = Point.Create(x0[0], x0[1], x0[2])
#------------End General-------------------

#---------------B1 - Cortical Bone----------
# Set outer dimensions of B1 (Cortical bone)
outerPointB1 = Point.Create(xb1[0], xb1[1], xb1[2])

# Create B1
result = BlockBody.Create(originPoint, outerPointB1)

# Rename 'Solid' to 'Cortical Bone' and redefine color
selection = BodySelection.Create(GetRootPart().Bodies[0])
result = RenameObject.Execute(selection,"Cortical Bone")
options = SetColorOptions()
options.FaceColorTarget = FaceColorTarget.Body
ColorHelper.SetColor(selection, options, ColorHelper.Magenta)
# EndBlock
#-----------End - B1 - Cortical Bone----------

#---------------B2 - Cancellous Bone----------
# Set origin for B2 (Trabecular bone)
x0b2 = [x0[0] + tb1, x0[1] + tb1, x0[2]]
originPointB2 = Point.Create(x0b2[0], x0b2[1], x0b2[2])

# Set parameters for outer dimensions of B2
xb2 = [xb1[0]  - tb1, xb1[1] - tb1, xb1[2]]
outerPointB2 = Point.Create(xb2[0], xb2[1], xb2[2])

# Create B2e
extTypInd = ExtrudeType.ForceIndependent
result = BlockBody.Create(originPointB2, outerPointB2, extTypInd)

# Rename 'Solid' to 'Cancellous Bone' and redifine color
selection = BodySelection.Create(GetRootPart().Bodies[1])
result = RenameObject.Execute(selection,"Cancellous Bone")
options = SetColorOptions()
options.FaceColorTarget = FaceColorTarget.Body
ColorHelper.SetColor(selection, options, Color.Gray)
# EndBlock
#-----------End - B2 - Cancellous Bone---------

#-------------------Implant--------------------
# Set Sketch Plane
sectionPlane = Plane.PlaneYZ
result = ViewHelper.SetSketchPlane(sectionPlane, None)
# EndBlock

# Create Sketch Cylinder
x0c1 = Point.Create(MM(0), hImp, MM(0))
x0c2 = Point.Create(MM(0), hImp, rImp)
result = CylinderBody.Create(originPoint, x0c1, x0c2, ExtrudeType.ForceIndependent)
# EndBlock

# Rename 'Solid' to 'Implant' and redefine color
selection = BodySelection.Create(GetRootPart().Bodies[2])
result = RenameObject.Execute(selection,"Implant")
options = SetColorOptions()
options.FaceColorTarget = FaceColorTarget.Body
ColorHelper.SetColor(selection, options, ColorHelper.Yellow)
# EndBlock
#-------------------End - Implant----------------------

if (not uniformDamage):
    #---------Periimplantitis Affected Region (PAR)---------
    # Sketch Ellipse for PAR
    origin = Point2D.Create(x0c2[1], -x0c2[2])
    majorDir = -DirectionUV.DirU
    minorDir = -DirectionUV.DirV
    result = SketchEllipse.Create(origin, majorDir, minorDir, pDamV, pDamH)
    # EndBlock

    # Sketch Trim Line
    start = Point2D.Create(origin[0], origin[1] + pDamH)
    end = Point2D.Create(origin[0],origin[1] - pDamH)
    result = SketchLine.Create(start, end)
    # EndBlock

    # Sketch Trim Line
    start = Point2D.Create(origin[0], origin[1])
    end = Point2D.Create(origin[0] - pDamV, origin[1])
    result = SketchLine.Create(start, end)
    # EndBlock

    # Solidify Sketch
    mode = InteractionMode.Solid
    result = ViewHelper.SetViewMode(mode, None)
    # EndBlock

    # Revolve 1 Face
    selection = FaceSelection.Create(GetRootPart().Bodies[3].Faces[2])
    axisSelection = Selection.Create(GetRootPart().CoordinateSystems[0].Axes[1])
    axis = RevolveFaces.GetAxisFromSelection(selection, axisSelection)
    options = RevolveFaceOptions()
    options.ExtrudeType = ExtrudeType.ForceIndependent
    result = RevolveFaces.Execute(selection, axis, DEG(360), options)
    # EndBlock

    # Delete Objects
    selection = BodySelection.Create(GetRootPart().Bodies[3])
    result = Delete.Execute(selection)
    # EndBlock

    # Rename 'Solid' to 'Periimplantitis Region' and redefine color
    selection = BodySelection.Create(GetRootPart().Bodies[3])
    result = RenameObject.Execute(selection,"Periimplantitis Region")
    options = SetColorOptions()
    options.FaceColorTarget = FaceColorTarget.Body
    ColorHelper.SetColor(selection, options, ColorHelper.Red)
    # EndBlock
    #---------End - Periimplantitis Region-------------

    #---------Remodelled Cortical Bone (RCB) Region-------
    # Set Sketch Plane
    sectionPlane = Plane.PlaneYZ
    result = ViewHelper.SetSketchPlane(sectionPlane, None)
    # EndBlock

    # Sketch Ellipse for RCB
    origin = Point2D.Create(x0c2[1], -x0c2[2])
    majorDir = -DirectionUV.DirU
    minorDir = -DirectionUV.DirV
    result = SketchEllipse.Create(origin, majorDir, minorDir, pDamV + tb1, pDamH + tb1)
    # EndBlock

    # Sketch Trim Line
    start = Point2D.Create(origin[0], origin[1] + pDamH + tb1)
    end = Point2D.Create(origin[0],origin[1] - pDamH - tb1)
    result = SketchLine.Create(start, end)
    # EndBlock

    # Sketch Trim Line
    start = Point2D.Create(origin[0], origin[1])
    end = Point2D.Create(origin[0] - pDamV - tb1, origin[1])
    result = SketchLine.Create(start, end)
    # EndBlock

    # Solidify Sketch
    mode = InteractionMode.Solid
    result = ViewHelper.SetViewMode(mode, None)
    # EndBlock

    # Revolve 1 Face
    selection = FaceSelection.Create(GetRootPart().Bodies[4].Faces[2])
    axisSelection = Selection.Create(GetRootPart().CoordinateSystems[0].Axes[1])
    axis = RevolveFaces.GetAxisFromSelection(selection, axisSelection)
    options = RevolveFaceOptions()
    options.ExtrudeType = ExtrudeType.ForceIndependent
    result = RevolveFaces.Execute(selection, axis, DEG(360), options)
    # EndBlock

    # Delete Objects
    selection = BodySelection.Create(GetRootPart().Bodies[4])
    result = Delete.Execute(selection)
    # EndBlock

    # Rename 'Solid' to 'Remodeled Cortical Bone' and redefine color
    selection = BodySelection.Create(GetRootPart().Bodies[4])
    result = RenameObject.Execute(selection,"Remodeled Cortical Bone")
    options = SetColorOptions()
    options.FaceColorTarget = FaceColorTarget.Body
    ColorHelper.SetColor(selection, options, ColorHelper.Blue)
    # EndBlock

    # Fill (Only if faces #6 and #7 actually exist)
    if (len(GetRootPart().Bodies[0].Faces) > 6):
        selection = FaceSelection.Create(GetRootPart().Bodies[0].Faces[6])
        secondarySelection = Selection.Empty()
        options = FillOptions()
        result = Fill.Execute(selection, secondarySelection, options, FillMode.ThreeD, None)
    # EndBlock

    #---------------End - Remodelled Cortical Bone Region-------------
    #-------------Move PAR + Remodelled Cortical Bone Region----------
    # Delta for moving created Implant + PAR + Remodelled Cortical Bone
    deltax = [xb1[0]/2, xb1[1] - hImp, xb1[2]/2]

    # Translate Along X Handle
    selection = BodySelection.Create([GetRootPart().Bodies[4], GetRootPart().Bodies[3]])
    direction = Direction.DirX
    options = MoveOptions()
    result = Move.Translate(selection, direction, deltax[0], options)
    # EndBlock

    # Translate Along Y Handle
    direction = Direction.DirY
    result = Move.Translate(selection, direction, deltax[1], options)
    # EndBlock

    # Translate Along Z Handle
    direction = Direction.DirZ
    result = Move.Translate(selection, direction, deltax[2], options)
    # EndBlock
    #---------End - Move PAR + Remodelled Cortical Bone Region----------
#-------------Move Implant Region----------
# Delta for moving created Implant
deltax = [xb1[0]/2, xb1[1] - hImp, xb1[2]/2]

# Translate Along X Handle
selection = BodySelection.Create([GetRootPart().Bodies[2]])
direction = Direction.DirX
options = MoveOptions()
result = Move.Translate(selection, direction, deltax[0], options)
# EndBlock

# Translate Along Y Handle
direction = Direction.DirY
result = Move.Translate(selection, direction, deltax[1], options)
# EndBlock

# Translate Along Z Handle
direction = Direction.DirZ
result = Move.Translate(selection, direction, deltax[2], options)
# EndBlock
#---------End - Move Implant Region----------
#------------------Execute boolean operations-----------------------
# Intersect Bodies
targets = BodySelection.Create(GetRootPart().Bodies[0], GetRootPart().Bodies[1])
tools = BodySelection.Create(GetRootPart().Bodies[2])
options = MakeSolidsOptions()
options.KeepCutter = False
result = Combine.Intersect(targets, tools, options)
# EndBlock

if (not uniformDamage):
    # Delete Objects
    selection = BodySelection.Create(GetRootPart().Bodies[4], GetRootPart().Bodies[5] )
    result = Combine.RemoveRegions(selection)
    # EndBlock

    # Intersect Bodies
    targets = BodySelection.Create(GetRootPart().Bodies[0])
    tools = BodySelection.Create(GetRootPart().Bodies[2])
    options = MakeSolidsOptions()
    options.KeepCutter = False
    result = Combine.Intersect(targets, tools, options)
    # EndBlock

    # Delete Objects
    selection = BodySelection.Create(GetRootPart().Bodies[3])
    result = Combine.RemoveRegions(selection)
    # EndBlock

    # Intersect Bodies
    targets = BodySelection.Create(GetRootPart().Bodies[1])
    tools = BodySelection.Create(GetRootPart().Bodies[2])
    options = MakeSolidsOptions()
    options.KeepCutter = False
    result = Combine.Intersect(targets, tools, options)
    # EndBlock

    # Delete Objects
    selection = BodySelection.Create(GetRootPart().Bodies[2])
    result = Combine.RemoveRegions(selection)
    # EndBlock
else:
    # Delete Objects
    selection = BodySelection.Create(GetRootPart().Bodies[2], GetRootPart().Bodies[3])
    result = Combine.RemoveRegions(selection)
    # EndBlock

# Intersect Bodies
targets = BodySelection.Create(GetRootPart().Bodies[0])
tools = BodySelection.Create(GetRootPart().Bodies[1])
options = MakeSolidsOptions()
result = Combine.Intersect(targets, tools, options)
 # EndBlock

# Delete Objects
selection = BodySelection.Create(GetRootPart().Bodies[2])
result = Combine.RemoveRegions(selection)
# EndBlock

#---------End - Execute boolean operations---------------
#---------Execute split operations (half model!)---------
# Create Origin
origin = Point.Create(xb1[0]/2, xb1[1]/2, xb1[2]/2)
x_Direction = -Direction.DirX
y_Direction = Direction.DirZ
result = DatumOriginCreator.Create(origin, x_Direction, y_Direction, None)
# EndBlock

# Create Datum Plane
selection = Selection.Create(GetRootPart().CoordinateSystems[0].Axes[1])
result = DatumPlaneCreator.Create(selection, False, None)
# EndBlock

# Slice Bodies by Plane
selection = BodySelection.Create(GetRootPart().Bodies[0])
datum = Selection.Create(GetRootPart().DatumPlanes[0])
result = SplitBody.ByCutter(selection, datum)
# EndBlock

# Delete Objects
selection = BodySelection.Create(GetRootPart().Bodies[2])
result = Combine.RemoveRegions(selection)
# EndBlock

# Slice Bodies by Plane
selection = BodySelection.Create(GetRootPart().Bodies[1])
datum = Selection.Create(GetRootPart().DatumPlanes[0])
result = SplitBody.ByCutter(selection, datum)
# EndBlock

# Delete Objects
selection = BodySelection.Create(GetRootPart().Bodies[2])
result = Combine.RemoveRegions(selection)
# EndBlock

# Delete Objects
selection = Selection.Create(GetRootPart().DatumPlanes[0])
result = Delete.Execute(selection)
# EndBlock

# Delete Objects
selection = Selection.Create(GetRootPart().CoordinateSystems[0])
result = Delete.Execute(selection)
# EndBlock

#------End - Execute split operations (half model!)-----
#------Insert Implant and Crown (i.e., existing models!)---
# Insert From File
os.chdir('G:')
importOptions = ImportOptions.Create()
DocumentInsert.Execute(r".\6_Ansys\A0003\Geometry\ImplantAbutment.scdoc", importOptions, GetMaps("d48edbd9"))
# EndBlock

if (not uniformDamage):
    faceIndexMove = [7, 6, 8, 9]
else:
    faceIndexMove = [7, 9, 5, 6]
        
# Move Upto Selected Object
selection = ComponentSelection.Create(GetRootPart().Components[0])
upToSelection = FaceSelection.Create(GetRootPart().Bodies[1].Faces[faceIndexMove[0]])
anchorPoint = Move.GetAnchorPoint(FaceSelection.Create(GetRootPart().Components[0].Content.Bodies[0].Faces[faceIndexMove[1]]))
options = MoveOptions()
result = Move.UpTo(selection, upToSelection, anchorPoint, options)
# EndBlock

# Move Upto Selected Object
selection = ComponentSelection.Create(GetRootPart().Components[0])
upToSelection = FaceSelection.Create(GetRootPart().Bodies[1].Faces[faceIndexMove[2]])
anchorPoint = Move.GetAnchorPoint(FaceSelection.Create(GetRootPart().Components[0].Content.Bodies[0].Faces[faceIndexMove[3]]))
options = MoveOptions()
result = Move.UpTo(selection, upToSelection, anchorPoint, options)
# EndBlock

# Insert From File
importOptions = ImportOptions.Create()
DocumentInsert.Execute(r".\6_Ansys\A0003\Geometry\Superstructure.scdoc", importOptions, GetMaps("e6720cc8"))
# EndBlock

# Move Upto Selected Object
selection = ComponentSelection.Create(GetRootPart().Components[1])
upToSelection = FaceSelection.Create(GetRootPart().Components[0].Content.Bodies[0].Faces[8])
anchorPoint = Move.GetAnchorPoint(FaceSelection.Create(GetRootPart().Components[1].Content.Bodies[0].Faces[1]))
options = MoveOptions()
result = Move.UpTo(selection, upToSelection, anchorPoint, options)
# EndBlock

# Move Upto Selected Object
selection = ComponentSelection.Create(GetRootPart().Components[1])
upToSelection = FaceSelection.Create(GetRootPart().Components[0].Content.Bodies[0].Faces[7])
anchorPoint = Move.GetAnchorPoint(FaceSelection.Create(GetRootPart().Components[1].Content.Bodies[0].Faces[0]))
options = MoveOptions()
result = Move.UpTo(selection, upToSelection, anchorPoint, options)
# EndBlock

# Move SYS\Implant and Abutment
selections = BodySelection.Create(GetRootPart().Components[0].Content.Bodies[0])
component = PartSelection.Create(GetRootPart())
result = ComponentHelper.MoveBodiesToComponent(selections, component, False, None)
# EndBlock

# Move SYS\Superstructure
selections = BodySelection.Create(GetRootPart().Components[1].Content.Bodies[0])
component = PartSelection.Create(GetRootPart())
result = ComponentHelper.MoveBodiesToComponent(selections, component, False, None)
# EndBlock


# Delete Objects
selection = ComponentSelection.Create([GetRootPart().Components[0],
    GetRootPart().Components[1]])
result = Delete.Execute(selection)
# EndBlock

# Rename 'SYS\Implant and Abutment' to 'Implant and Abutment'
selection = BodySelection.Create(GetRootPart().Bodies[2])
result = RenameObject.Execute(selection,"Implant and Abutment")
# EndBlock

# Rename 'SYS\Superstructure' to 'Superstructure'
selection = BodySelection.Create(GetRootPart().Bodies[3])
result = RenameObject.Execute(selection,"Superstructure")
# EndBlock
#----End - Insert Implant and Crown (i.e., existing models!)---
#---------------Create Named Selections------------------------
# Create Named Selection Group
primarySelection = FaceSelection.Create([GetRootPart().Bodies[1].Faces[0],
    GetRootPart().Bodies[0].Faces[0]])
secondarySelection = Selection.Empty()
result = NamedSelection.Create(primarySelection, secondarySelection)
# EndBlock

# Rename Named Selection
result = NamedSelection.Rename("Group1", "Mesial Bone Surface")
result = NamedSelection.Rename("Gruppe1", "Mesial Bone Surface")
# EndBlock


# Create Named Selection Group
primarySelection = FaceSelection.Create([GetRootPart().Bodies[3].Faces[5],
    GetRootPart().Bodies[2].Faces[10],
    GetRootPart().Bodies[0].Faces[1],
    GetRootPart().Bodies[1].Faces[1]])
secondarySelection = Selection.Empty()
result = NamedSelection.Create(primarySelection, secondarySelection)
# EndBlock

# Rename Named Selection
result = NamedSelection.Rename("Group1", "Symmetry Plane Surface")
result = NamedSelection.Rename("Gruppe1", "Symmetry Plane Surface")
# EndBlock


# Create Named Selection Group
primarySelection = FaceSelection.Create(GetRootPart().Bodies[3].Faces[2])
secondarySelection = Selection.Empty()
result = NamedSelection.Create(primarySelection, secondarySelection)
# EndBlock

# Rename Named Selection
result = NamedSelection.Rename("Group1", "Load Application Surface")
result = NamedSelection.Rename("Gruppe1", "Load Application Surface")
# EndBlock

# Loop for creation of named selection for each body
for i in range(len(GetRootPart().Bodies)):
    # Create Named Selection Group
    primarySelection = BodySelection.Create(GetRootPart().Bodies[i])
    secondarySelection = Selection.Empty()
    result = NamedSelection.Create(primarySelection, secondarySelection)
    # EndBlock

    # Rename Named Selection
    result = NamedSelection.Rename("Group1", GetRootPart().Bodies[i].GetName() + " NS")
    result = NamedSelection.Rename("Gruppe1", GetRootPart().Bodies[i].GetName() + " NS")
    # EndBlock
#----------------End - Create Named Selections-----------------