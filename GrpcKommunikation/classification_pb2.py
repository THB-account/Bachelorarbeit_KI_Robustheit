# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: classification.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import GrpcKommunikation.data_pb2 as data__pb2
import GrpcKommunikation.metadata_pb2 as metadata__pb2
import GrpcKommunikation.recording_pb2 as recording__pb2
import GrpcKommunikation.sensor_pb2 as sensor__pb2
import GrpcKommunikation.specifications_pb2 as specifications__pb2
import GrpcKommunikation.util_pb2 as util__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14\x63lassification.proto\x12\x11logbee.anne.model\x1a\ndata.proto\x1a\x0emetadata.proto\x1a\x0frecording.proto\x1a\x0csensor.proto\x1a\x14specifications.proto\x1a\nutil.proto\"\'\n\x10\x43lassificationId\x12\x13\n\x04uuid\x18\x01 \x01(\x0b\x32\x05.UUID\"j\n\x18\x43lassificationDescriptor\x12/\n\x02id\x18\x01 \x01(\x0b\x32#.logbee.anne.model.ClassificationId\x12\x1d\n\nproperties\x18\x02 \x03(\x0b\x32\t.Property\"*\n\x13\x43lassificationJobId\x12\x13\n\x04uuid\x18\x01 \x01(\x0b\x32\x05.UUID\"\x91\x02\n\x19\x43lassificationJobMetadata\x12\x32\n\x02id\x18\x01 \x01(\x0b\x32&.logbee.anne.model.ClassificationJobId\x12\x1f\n\trecording\x18\x02 \x01(\x0b\x32\x0c.RecordingId\x12\x1d\n\x08scenario\x18\x03 \x01(\x0b\x32\x0b.ScenarioId\x12\x0c\n\x04step\x18\x04 \x01(\r\x12\x19\n\x06sensor\x18\x05 \x01(\x0b\x32\t.SensorId\x12\x1c\n\x14\x63hunkStartOffsetNano\x18\x06 \x01(\x04\x12\x1a\n\x12\x63hunkEndOffsetNano\x18\x07 \x01(\x04\x12\x1d\n\nproperties\x18\x08 \x03(\x0b\x32\t.Property\"\xa1\x01\n\x11\x43lassificationJob\x12>\n\x08metadata\x18\x01 \x01(\x0b\x32,.logbee.anne.model.ClassificationJobMetadata\x12\x1d\n\taudioData\x18\x02 \x01(\x0b\x32\n.AudioData\x12-\n\x11\x61\x63\x63\x65lerometerData\x18\x03 \x01(\x0b\x32\x12.AccelerometerData\"\xad\x01\n\x15\x43lassificationOutcome\x12\x41\n\x0bjobMetadata\x18\x01 \x01(\x0b\x32,.logbee.anne.model.ClassificationJobMetadata\x12\x32\n\x0bpredictions\x18\x02 \x03(\x0b\x32\x1d.logbee.anne.model.Prediction\x12\x1d\n\nproperties\x18\x03 \x03(\x0b\x32\t.Property\"\x97\x01\n\nPrediction\x12\x33\n\x06result\x18\x01 \x01(\x0b\x32#.logbee.anne.model.PredictionResult\x12\x12\n\nconfidence\x18\x02 \x01(\x02\x12!\n\x19pointOfInterestOffsetNano\x18\x03 \x01(\x04\x12\x1d\n\nproperties\x18\x04 \x03(\x0b\x32\t.Property\"\x87\x01\n\x10PredictionResult\x12\x33\n\x02ok\x18\x01 \x01(\x0b\x32%.logbee.anne.model.PredictionResultOkH\x00\x12\x35\n\x03nok\x18\x02 \x01(\x0b\x32&.logbee.anne.model.PredictionResultNokH\x00\x42\x07\n\x05value\"\x14\n\x12PredictionResultOk\"\x15\n\x13PredictionResultNokB@\n)com.daimler.smartfactory.anne.model.protoB\x13\x43lassificationProtob\x06proto3')



_CLASSIFICATIONID = DESCRIPTOR.message_types_by_name['ClassificationId']
_CLASSIFICATIONDESCRIPTOR = DESCRIPTOR.message_types_by_name['ClassificationDescriptor']
_CLASSIFICATIONJOBID = DESCRIPTOR.message_types_by_name['ClassificationJobId']
_CLASSIFICATIONJOBMETADATA = DESCRIPTOR.message_types_by_name['ClassificationJobMetadata']
_CLASSIFICATIONJOB = DESCRIPTOR.message_types_by_name['ClassificationJob']
_CLASSIFICATIONOUTCOME = DESCRIPTOR.message_types_by_name['ClassificationOutcome']
_PREDICTION = DESCRIPTOR.message_types_by_name['Prediction']
_PREDICTIONRESULT = DESCRIPTOR.message_types_by_name['PredictionResult']
_PREDICTIONRESULTOK = DESCRIPTOR.message_types_by_name['PredictionResultOk']
_PREDICTIONRESULTNOK = DESCRIPTOR.message_types_by_name['PredictionResultNok']
ClassificationId = _reflection.GeneratedProtocolMessageType('ClassificationId', (_message.Message,), {
  'DESCRIPTOR' : _CLASSIFICATIONID,
  '__module__' : 'classification_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.model.ClassificationId)
  })
_sym_db.RegisterMessage(ClassificationId)

ClassificationDescriptor = _reflection.GeneratedProtocolMessageType('ClassificationDescriptor', (_message.Message,), {
  'DESCRIPTOR' : _CLASSIFICATIONDESCRIPTOR,
  '__module__' : 'classification_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.model.ClassificationDescriptor)
  })
_sym_db.RegisterMessage(ClassificationDescriptor)

ClassificationJobId = _reflection.GeneratedProtocolMessageType('ClassificationJobId', (_message.Message,), {
  'DESCRIPTOR' : _CLASSIFICATIONJOBID,
  '__module__' : 'classification_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.model.ClassificationJobId)
  })
_sym_db.RegisterMessage(ClassificationJobId)

ClassificationJobMetadata = _reflection.GeneratedProtocolMessageType('ClassificationJobMetadata', (_message.Message,), {
  'DESCRIPTOR' : _CLASSIFICATIONJOBMETADATA,
  '__module__' : 'classification_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.model.ClassificationJobMetadata)
  })
_sym_db.RegisterMessage(ClassificationJobMetadata)

ClassificationJob = _reflection.GeneratedProtocolMessageType('ClassificationJob', (_message.Message,), {
  'DESCRIPTOR' : _CLASSIFICATIONJOB,
  '__module__' : 'classification_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.model.ClassificationJob)
  })
_sym_db.RegisterMessage(ClassificationJob)

ClassificationOutcome = _reflection.GeneratedProtocolMessageType('ClassificationOutcome', (_message.Message,), {
  'DESCRIPTOR' : _CLASSIFICATIONOUTCOME,
  '__module__' : 'classification_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.model.ClassificationOutcome)
  })
_sym_db.RegisterMessage(ClassificationOutcome)

Prediction = _reflection.GeneratedProtocolMessageType('Prediction', (_message.Message,), {
  'DESCRIPTOR' : _PREDICTION,
  '__module__' : 'classification_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.model.Prediction)
  })
_sym_db.RegisterMessage(Prediction)

PredictionResult = _reflection.GeneratedProtocolMessageType('PredictionResult', (_message.Message,), {
  'DESCRIPTOR' : _PREDICTIONRESULT,
  '__module__' : 'classification_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.model.PredictionResult)
  })
_sym_db.RegisterMessage(PredictionResult)

PredictionResultOk = _reflection.GeneratedProtocolMessageType('PredictionResultOk', (_message.Message,), {
  'DESCRIPTOR' : _PREDICTIONRESULTOK,
  '__module__' : 'classification_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.model.PredictionResultOk)
  })
_sym_db.RegisterMessage(PredictionResultOk)

PredictionResultNok = _reflection.GeneratedProtocolMessageType('PredictionResultNok', (_message.Message,), {
  'DESCRIPTOR' : _PREDICTIONRESULTNOK,
  '__module__' : 'classification_pb2'
  # @@protoc_insertion_point(class_scope:logbee.anne.model.PredictionResultNok)
  })
_sym_db.RegisterMessage(PredictionResultNok)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n)com.daimler.smartfactory.anne.model.protoB\023ClassificationProto'
  _CLASSIFICATIONID._serialized_start=136
  _CLASSIFICATIONID._serialized_end=175
  _CLASSIFICATIONDESCRIPTOR._serialized_start=177
  _CLASSIFICATIONDESCRIPTOR._serialized_end=283
  _CLASSIFICATIONJOBID._serialized_start=285
  _CLASSIFICATIONJOBID._serialized_end=327
  _CLASSIFICATIONJOBMETADATA._serialized_start=330
  _CLASSIFICATIONJOBMETADATA._serialized_end=603
  _CLASSIFICATIONJOB._serialized_start=606
  _CLASSIFICATIONJOB._serialized_end=767
  _CLASSIFICATIONOUTCOME._serialized_start=770
  _CLASSIFICATIONOUTCOME._serialized_end=943
  _PREDICTION._serialized_start=946
  _PREDICTION._serialized_end=1097
  _PREDICTIONRESULT._serialized_start=1100
  _PREDICTIONRESULT._serialized_end=1235
  _PREDICTIONRESULTOK._serialized_start=1237
  _PREDICTIONRESULTOK._serialized_end=1257
  _PREDICTIONRESULTNOK._serialized_start=1259
  _PREDICTIONRESULTNOK._serialized_end=1280
# @@protoc_insertion_point(module_scope)
