##
#	\namespace	cross3d.constants
#
#	\remarks	This package defines all the constant Enum types that will be used throughout the blur3d package
#
#	\author		eric
#	\author		Blur Studio
#	\date		03/15/10
#

from enum import Enum

# A

AnimationType = Enum('FCurve', 'StaticFCurve', 'Expression', 'Transforms', 'Position', 'Rotation', 'Scale', 'Layer')

# B

# C

CameraType = Enum('Standard', 'VRayPhysical', 'Physical')
CacheType = Enum('Point_Cache', 'Transform_Cache', 'XmeshLoader')
CloneType = Enum('Copy', 'Instance', 'Reference')
ControllerType = Enum('BezierFloat', 'LinearFloat', 'ScriptFloat', 'AlembicFloat')

# D

class _DebugLevel(Enum): pass
class DebugLevels(EnumGroup):
	Disabled = _DebugLevel(0)
	Low = _DebugLevel()
	Mid = _DebugLevel()
	High = _DebugLevel()

DepartmentGroup = Enum('All', 'Simulation', 'PostPerformance', 'Performance', 'Rendering')

# E

ExtrapolationType = Enum('Constant', 'Linear', 'Cycled', 'CycledWithOffset', 'PingPong')

class EnvironmentType(Enum): pass
class EnvironmentTypes(EnumGroup):
	Unknown = EnvironmentType()
	Atmospheric = EnvironmentType()
	Effect = EnvironmentType()

# F

FPSChangeType = Enum('Frames', 'Seconds')
FPSContext = Enum('Project', 'Sequence', 'Shot')
FPSChangeType.setDescription(FPSChangeType.Frames, 'Timings fixed on frames, animation curves scaled to compensate.')
FPSChangeType.setDescription(FPSChangeType.Seconds, 'Timings fixed on seconds, animation key values in frame will change.')

# G

# H

# I

IODirection = Enum('Input', 'Output', InAndOut=3)

# J

# K

TangentType = Enum('Automatic', 'Bezier', 'Linear', 'Stepped')

# L

# M

MaterialType = Enum('Generic', 'VRay')
MaterialCacheType = Enum('BaseMaterial', 'MaterialOverrideList')
MaterialOverrideOptions = Enum('KeepOpacity', 'KeepDisplacement', 'KeepBump', All=3)
MapCacheType = Enum('EnvironmentMap')
MapType = Enum('Generic', 'VRay')
MaterialPropertyMap = Enum(outColor='diffuse')

# N

NotifyType = Enum('Email', 'Jabber')

# O

ObjectType = Enum(
	'Generic',
	'Geometry',
	'Light',
	'Camera',
	'Model',
	'Group',
	'Bone',
	'Particle',
	'FumeFX',
	'Curve',
	'PolyMesh',
	'NurbsSurface',
	'Thinking',
	'XMeshLoader',
	'CameraInterest',
	'Null'
)

# P
class PointerType(Enum): pass
class PointerTypes(EnumGroup):
	Shape = PointerType()
	Transform = PointerType()
	Pointer = PointerType()
	
ProxyType = Enum('Disabled', 'Lossy', 'Lossless')
PaddingStyle = Enum('Blank', 'Number', 'Pound', 'Percent', 'Wildcard')

# Q

# R

RendererType = Enum('Scanline', 'VRay', 'MentalRay', 'Quicksilver')
RotationOrder = Enum('XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX')

class RigMake(Enum):
	pass

class RigMakes(EnumGroup):
	Biped = RigMake()
	HumanIK = RigMake()
	CAT = RigMake()
	MadCar = RigMake()
	Harbie = RigMake()
	Gear = RigMake()
	BradNoble = RigMake()

# S

ScriptLanguage = Enum('Python', 'MAXScript', 'JavaScript', 'VisualBasic', 'MEL')
SubmitType = Enum('Render', 'Script', 'Batch')
SubmitFlags = Enum('WriteInfoFile', 'DeleteOldFrames', 'VisibleToRenderable', 'RemoteSubmit', 'DeleteHiddenGeometry', 'CreateProxyJob', Default=1)
Source = Enum('Remote', 'Local')

# T

TimeUnit = Enum('Frames', 'Seconds', 'Milliseconds', 'Ticks')

# U

UpVector = Enum('Y', 'Z')

# V

VideoCodec = Enum('PhotoJPEG', 'H264', 'GIF')
Viewports = Enum('Current', 'One', 'Two', 'Three', 'Four')
VisibilityToggleOptions = Enum(
	'ToggleLights',
	'ToggleFX',
	'ToggleAtmospherics',
	'TogglePointCaches',
	'ToggleTransformCaches',
	'ToggleXMeshes',
	'ToggleFrost',
	'ToggleVRayStereoscopics',
	'ToggleAlembic',
	All=511
)

# W

# X

# Y

# Z
